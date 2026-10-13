"""Train and check a wastewater subtype classifier on NCBI BioSample candidates.

Labels come from rules (inflow, effluent, sludge, digester, sewer). The words that
produce a label are removed from the text before training, so the model has to learn
from the rest of each record. That is what lets it say anything about samples the
rules leave unlabeled. Evaluation holds out whole BioProjects.

Inputs (local MongoDB, built by the mongo-js scripts for issue 570 and 580):
wastewater_biosample_candidates and wastewater_flow_labels.

Related: https://github.com/microbiomedata/external-metadata-awareness/issues/580
"""

import json
import logging
from pathlib import Path

import click
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import GroupShuffleSplit

from external_metadata_awareness.mongodb_connection import get_mongo_client

logger = logging.getLogger(__name__)

TEXT_FIELDS = ["env_broad_scale", "env_local_scale", "env_medium", "isolation_source", "description_title"]

# Same wording as mongo-js/wastewater_bioproject_table.js and wastewater_sample_name_flow_check.js
INFLOW = r"(?<!surface water )influent|inflow|in-flow|raw (?:sewage|wastewater|waste water)|untreated (?:sewage|wastewater|waste water)|plant inlet|\binlet\b"
OUTFLOW = r"effluent|outflow|outfall|(?<!un)treated (?:sewage|wastewater|waste water)|discharge"
NAME_INFLOW_TOKENS = r"(?<![A-Za-z])(?:IN|INF|INFL|Inf|Infl)(?![A-Za-z])"
NAME_OUTFLOW_TOKENS = r"(?<![A-Za-z])(?:EF|EFF|Eff|OUT)(?![A-Za-z])"
SLUDGE = r"sludge|mixed liquor|biosolid"
DIGESTER = r"digest(?:er|or|ate|ion)|biogas"
SEWER = r"\bsewers?\b|sewer pipe|manhole|sewershed|pump(?:ing)? station|lift station"

# A digester sample often says "anaerobic sludge"; count it as digester only
SUBTYPES = ["inflow", "effluent", "sludge", "digester", "sewer"]
MASKS = [INFLOW, OUTFLOW, SLUDGE, DIGESTER, SEWER]


def rule_labels(df: pd.DataFrame) -> pd.DataFrame:
    """One boolean column per subtype, from the flow flags and the subtype wording."""
    text = df["text_raw"]
    labels = pd.DataFrame(index=df.index)
    labels["inflow"] = df["field_inflow"] | df["name_inflow_words"] | df["name_inflow_tokens"]
    labels["effluent"] = df["field_outflow"] | df["name_outflow_words"] | df["name_outflow_tokens"]
    labels["digester"] = text.str.contains(DIGESTER, case=False, regex=True)
    labels["sludge"] = text.str.contains(SLUDGE, case=False, regex=True) & ~labels["digester"]
    labels["sewer"] = text.str.contains(SEWER, case=False, regex=True)
    return labels


def mask(text: pd.Series) -> pd.Series:
    """Remove every word that a rule uses, plus the sample-name flow tokens."""
    out = text
    for pattern in MASKS:
        out = out.str.replace(pattern, " ", case=False, regex=True)
    for pattern in (NAME_INFLOW_TOKENS, NAME_OUTFLOW_TOKENS):
        out = out.str.replace(pattern, " ", regex=True)
    return out.str.replace(r"\s+", " ", regex=True).str.strip()


def project_groups(bioprojects: pd.Series) -> list[str | None]:
    """One group per set of BioProjects that share a sample, so a held-out project shares no sample with training."""
    parent: dict[str, str] = {}

    def find(a: str) -> str:
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for bps in bioprojects:
        if isinstance(bps, list) and bps:
            root = find(bps[0])
            for other in bps[1:]:
                parent[find(other)] = root
    return [find(bps[0]) if isinstance(bps, list) and bps else None for bps in bioprojects]


def load(mongo_uri: str, env_file: str | None) -> pd.DataFrame:
    client = get_mongo_client(mongo_uri, env_file)
    db = client.get_default_database()
    fields = {"_id": 0, "accession": 1, "package_content": 1, **{f: 1 for f in TEXT_FIELDS}}
    cand = pd.DataFrame(list(db.wastewater_biosample_candidates.find({}, fields)))
    flags = pd.DataFrame(list(db.wastewater_flow_labels.find({}, {"_id": 0})))
    df = cand.merge(flags, on="accession", how="inner")
    for f in TEXT_FIELDS + ["sample_name", "package_content"]:
        df[f] = df[f].fillna("").astype(str) if f in df else ""
    df["text_raw"] = df[TEXT_FIELDS + ["sample_name"]].agg(" | ".join, axis=1)
    # Samples with no BioProject get no group; they are used for training only
    df["group"] = project_groups(df["bioprojects"])
    return df


@click.command()
@click.option("--mongo-uri", envvar="MONGO_URI", required=True, help="URI including the database, e.g. mongodb://localhost:27017/ncbi_metadata")
@click.option("--env-file", default=None, help="Optional .env with MONGO_USER and MONGO_PASSWORD")
@click.option("--out-dir", type=click.Path(path_type=Path), default=Path("local/wastewater_subtype"), show_default=True)
@click.option("--threshold", default=0.8, show_default=True, help="Probability for counting a prediction on unlabeled samples")
@click.option("--seed", default=0, show_default=True)
def main(mongo_uri: str, env_file: str | None, out_dir: Path, threshold: float, seed: int) -> None:
    """Train one classifier per wastewater subtype and report held-out agreement with the rules."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    out_dir.mkdir(parents=True, exist_ok=True)
    df = load(mongo_uri, env_file)
    labels = rule_labels(df)
    text = mask(df["text_raw"])
    logger.info("samples %d, with any rule label %d", len(df), int(labels.any(axis=1).sum()))

    linked = np.flatnonzero(df["group"].notna().to_numpy())
    unlinked = np.flatnonzero(df["group"].isna().to_numpy())
    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed).split(linked, groups=df["group"].iloc[linked]))
    train_idx, test_idx = np.concatenate([linked[tr], unlinked]), linked[te]
    # Words of three or more letters only: character n-grams and digits let the model memorize sample-ID schemes of single projects
    vec = TfidfVectorizer(analyzer="word", token_pattern=r"(?u)\b[^\W\d_]{3,}\b", ngram_range=(1, 2), min_df=20, max_features=200_000, sublinear_tf=True, lowercase=True)
    x_train = vec.fit_transform(text.iloc[train_idx])
    x_all = vec.transform(text)
    wwsurv = df["package_content"].str.contains("wwsurv", regex=False).to_numpy()

    report, unlabeled = [], ~labels.any(axis=1).to_numpy()
    held_out = pd.DataFrame({"accession": df["accession"].iloc[test_idx].to_numpy(), "group": df["group"].iloc[test_idx].to_numpy(),
                             "wwsurv": wwsurv[test_idx], "rule_unlabeled": unlabeled[test_idx]})
    for subtype in SUBTYPES:
        y = labels[subtype].to_numpy()
        model = LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear")
        model.fit(x_train, y[train_idx])
        prob = model.predict_proba(x_all)[:, 1]
        held_out[f"rule_{subtype}"] = y[test_idx]
        held_out[f"prob_{subtype}"] = prob[test_idx].round(4)
        row = {"subtype": subtype, "rule_positive": int(y.sum()), "held_out_positive_groups": int(df["group"].iloc[test_idx][y[test_idx]].nunique())}
        for name, sel in (("held_out", test_idx), ("held_out_not_wwsurv", test_idx[~wwsurv[test_idx]])):
            p, r, f, _ = precision_recall_fscore_support(y[sel], prob[sel] >= 0.5, average="binary", zero_division=0)
            row.update({f"{name}_positive": int(y[sel].sum()), f"{name}_precision": round(p, 3), f"{name}_recall": round(r, 3), f"{name}_f1": round(f, 3)})
        row["unlabeled_predicted"] = int((prob[unlabeled] >= threshold).sum())
        report.append(row)
        # Highest-scoring unlabeled samples, for reading by eye
        candidates = np.flatnonzero(unlabeled)
        top = candidates[np.argsort(-prob[candidates])[:200]]
        pd.DataFrame({"accession": df["accession"].iloc[top], "probability": prob[top].round(3), "group": df["group"].iloc[top],
                      "text": df["text_raw"].iloc[top]}).to_csv(out_dir / f"unlabeled_top_{subtype}.tsv", sep="\t", index=False)
        terms = np.array(vec.get_feature_names_out())[np.argsort(-model.coef_[0])[:25]]
        logger.info("%s top features: %s", subtype, ", ".join(repr(t) for t in terms))

    pd.DataFrame(report).to_csv(out_dir / "report.tsv", sep="\t", index=False)
    # Scores for every held-out sample, for building and scoring a hand-checked set
    held_out.to_csv(out_dir / "held_out_predictions.tsv", sep="\t", index=False)
    (out_dir / "run.json").write_text(json.dumps({"seed": seed, "threshold": threshold, "train": len(train_idx), "test": len(test_idx), "train_without_bioproject": len(unlinked)}, indent=2))
    click.echo(pd.DataFrame(report).to_string(index=False))


if __name__ == "__main__":
    main()
