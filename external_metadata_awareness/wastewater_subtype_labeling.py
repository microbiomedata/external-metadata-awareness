"""Draw and score a hand-checked set for the wastewater subtype classifier.

`sample` draws held-out samples that the rules leave unlabeled, stratified by
classifier score, and writes a labeling sheet without the scores plus a separate key.
`score` compares the filled-in labels with the classifier and with a second labeler.

Labels follow docs/wastewater-subtype-labeling-guide.md.
Related: https://github.com/microbiomedata/external-metadata-awareness/issues/580
"""

import logging
from pathlib import Path

import click
import numpy as np
import pandas as pd

from external_metadata_awareness.mongodb_connection import get_mongo_client
from external_metadata_awareness.wastewater_subtype_classifier import SUBTYPES, TEXT_FIELDS

logger = logging.getLogger(__name__)

# Score bands per subtype, and how many samples to draw from each
BANDS = [(0.8, 1.01, 25), (0.5, 0.8, 15), (0.2, 0.5, 10)]
RANDOM_EXTRA = 50
MAX_PER_GROUP = 3


@click.group()
def main() -> None:
    """Hand-checked set for the wastewater subtype classifier."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")


@main.command()
@click.option("--mongo-uri", envvar="MONGO_URI", required=True, help="URI including the database")
@click.option("--env-file", default=None)
@click.option("--predictions", type=click.Path(exists=True, path_type=Path), required=True, help="held_out_predictions.tsv from wastewater-subtype-classifier")
@click.option("--sheet", type=click.Path(path_type=Path), required=True, help="Labeling sheet to write (no scores)")
@click.option("--key", type=click.Path(path_type=Path), required=True, help="Key to write (scores and strata)")
@click.option("--seed", default=0, show_default=True)
def sample(mongo_uri: str, env_file: str | None, predictions: Path, sheet: Path, key: Path, seed: int) -> None:
    """Draw the set from held-out samples the rules leave unlabeled."""
    rng = np.random.default_rng(seed)
    pred = pd.read_csv(predictions, sep="\t")
    pool = pred[pred["rule_unlabeled"]].copy()
    picked: dict[str, str] = {}

    def take(frame: pd.DataFrame, n: int, stratum: str) -> None:
        frame = frame[~frame["accession"].isin(picked)]
        # At most MAX_PER_GROUP from one BioProject group, so one project can't fill a band
        frame = frame.sample(frac=1, random_state=int(rng.integers(1 << 31))).groupby("group").head(MAX_PER_GROUP)
        for acc in frame["accession"].head(n):
            picked[acc] = stratum

    for subtype in SUBTYPES:
        for lo, hi, n in BANDS:
            take(pool[(pool[f"prob_{subtype}"] >= lo) & (pool[f"prob_{subtype}"] < hi)], n, f"{subtype} {lo}-{min(hi, 1.0)}")
    take(pool, RANDOM_EXTRA, "random")

    keyframe = pool[pool["accession"].isin(picked)].copy()
    keyframe["stratum"] = keyframe["accession"].map(picked)
    keyframe = keyframe.sample(frac=1, random_state=seed).reset_index(drop=True)
    keyframe.insert(0, "item", range(1, len(keyframe) + 1))

    db = get_mongo_client(mongo_uri, env_file).get_default_database()
    fields = {"_id": 0, "accession": 1, **{f: 1 for f in TEXT_FIELDS}}
    text = pd.DataFrame(list(db.wastewater_biosample_candidates.find({"accession": {"$in": list(picked)}}, fields)))
    names = pd.DataFrame(list(db.wastewater_flow_labels.find({"accession": {"$in": list(picked)}}, {"_id": 0, "accession": 1, "sample_name": 1})))
    out = keyframe[["item", "accession"]].merge(text, on="accession", how="left").merge(names, on="accession", how="left")
    out = out.reindex(columns=["item", "accession", *TEXT_FIELDS, "sample_name"]).fillna("")
    for col in ["labels", "lab_scale", "note"]:
        out[col] = ""
    out.to_csv(sheet, sep="\t", index=False)
    keyframe.to_csv(key, sep="\t", index=False)
    click.echo(f"{len(out)} samples; strata: {keyframe['stratum'].str.split().str[0].value_counts().to_dict()}")


@main.command()
@click.option("--sheet", type=click.Path(exists=True, path_type=Path), required=True, help="Labeled sheet (labels column, comma-separated)")
@click.option("--key", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--other", type=click.Path(exists=True, path_type=Path), default=None, help="A second labeler's sheet, to measure agreement")
@click.option("--threshold", default=0.5, show_default=True)
def score(sheet: Path, key: Path, other: Path | None, threshold: float) -> None:
    """Precision and recall of the classifier against the hand labels, per subtype."""
    lab = pd.read_csv(sheet, sep="\t", dtype=str).fillna("")
    k = pd.read_csv(key, sep="\t")
    df = k.merge(lab[["item", "labels"]].assign(item=lambda d: d["item"].astype(int)), on="item")
    sets = df["labels"].str.lower().str.replace(" ", "").str.split(",").apply(set)
    rows = []
    for subtype in SUBTYPES:
        gold = sets.apply(lambda s: subtype in s).to_numpy()
        pred = (df[f"prob_{subtype}"] >= threshold).to_numpy()
        tp = int((gold & pred).sum())
        rows.append({"subtype": subtype, "hand_positive": int(gold.sum()), "predicted": int(pred.sum()), "true_positive": tp,
                     "precision": round(tp / pred.sum(), 3) if pred.sum() else None, "recall": round(tp / gold.sum(), 3) if gold.sum() else None})
    click.echo(pd.DataFrame(rows).to_string(index=False))
    click.echo("labels: " + str(pd.Series([x for s in sets for x in s]).value_counts().to_dict()))
    if other is not None:
        o = pd.read_csv(other, sep="\t", dtype=str).fillna("")
        o_sets = o.set_index(o["item"].astype(int))["labels"].str.lower().str.replace(" ", "").str.split(",").apply(set)
        same = [s == o_sets.get(i, set()) for i, s in zip(df["item"], sets)]
        click.echo(f"exact label-set agreement with the other labeler: {sum(same)} of {len(same)}")
