"""Unit tests for the wastewater subtype classifier helpers (no MongoDB needed)."""

import pandas as pd
from click.testing import CliRunner

from external_metadata_awareness.wastewater_subtype_classifier import main, mask, project_groups, rule_labels


def test_projects_sharing_a_sample_form_one_group():
    groups = project_groups(pd.Series([["PRJNA2", "PRJNA1"], ["PRJNA1", "PRJNA3"], ["PRJNA9"]]))
    assert groups[0] == groups[1] == "PRJNA1"
    assert groups[2] == "PRJNA9"


def test_group_name_does_not_depend_on_order():
    a = project_groups(pd.Series([["PRJNA2", "PRJNA1"], ["PRJNA3", "PRJNA2"]]))
    b = project_groups(pd.Series([["PRJNA3", "PRJNA2"], ["PRJNA1", "PRJNA2"]]))
    assert set(a) == set(b) == {"PRJNA1"}


def test_samples_without_a_bioproject_get_no_group():
    assert project_groups(pd.Series([[], None, ["PRJNA1"]])) == [None, None, "PRJNA1"]


def test_mask_removes_rule_words_and_flow_tokens():
    text = pd.Series(["raw sewage | activated sludge | JNW-IN_Virome | anaerobic digester"])
    out = mask(text)[0]
    for word in ["raw sewage", "sludge", "digester", "-IN_"]:
        assert word not in out


def test_digester_wording_wins_over_sludge():
    df = pd.DataFrame({"text_raw": ["anaerobic digester sludge", "activated sludge"], "field_inflow": [False, False],
                       "field_outflow": [False, False], "name_inflow_words": [False, False], "name_inflow_tokens": [False, False],
                       "name_outflow_words": [False, False], "name_outflow_tokens": [False, False]})
    labels = rule_labels(df)
    assert labels["digester"].tolist() == [True, False]
    assert labels["sludge"].tolist() == [False, True]


def test_threshold_outside_zero_to_one_is_rejected():
    result = CliRunner().invoke(main, ["--mongo-uri", "mongodb://localhost:27017/x", "--threshold", "1.5"])
    assert result.exit_code != 0
    assert "1.5" in result.output


def test_hold_out_keeps_named_samples_out_of_training(tmp_path):
    from external_metadata_awareness.wastewater_subtype_classifier import split

    df = pd.DataFrame({"accession": [f"S{i}" for i in range(12)],
                       "group": ["P1", "P1", "P2", "P2", "P3", "P3", "P4", "P4", "P5", "P5", None, None]})
    hold = tmp_path / "hold.tsv"
    pd.DataFrame({"accession": ["S0", "S10"]}).to_csv(hold, sep="\t", index=False)
    train_idx, test_idx = split(df, 0, hold)
    assert {0, 1, 10} <= set(test_idx)
    assert not ({0, 1, 10} & set(train_idx))
    assert 11 in train_idx
    assert sorted(list(train_idx) + list(test_idx)) == list(range(12))


def test_score_reads_predictions_without_item_numbers(tmp_path):
    from external_metadata_awareness.wastewater_subtype_labeling import main as labeling

    sheet, preds = tmp_path / "sheet.tsv", tmp_path / "preds.tsv"
    pd.DataFrame({"item": [1, 2], "accession": ["S1", "S2"], "labels": ["digester", "unclear"]}).to_csv(sheet, sep="\t", index=False)
    probs = {f"prob_{s}": [0.0, 0.0] for s in ["inflow", "effluent", "sludge", "sewer"]}
    pd.DataFrame({"accession": ["S2", "S1"], "prob_digester": [0.1, 0.9], **probs}).to_csv(preds, sep="\t", index=False)
    result = CliRunner().invoke(labeling, ["score", "--sheet", str(sheet), "--key", str(preds)])
    assert result.exit_code == 0, result.output
    digester = next(line for line in result.output.splitlines() if line.strip().startswith("digester"))
    assert digester.split()[1:5] == ["1", "1", "0", "1"]


def test_score_rejects_blank_unknown_or_mixed_labels(tmp_path):
    from external_metadata_awareness.wastewater_subtype_labeling import main as labeling

    preds = tmp_path / "preds.tsv"
    pd.DataFrame({"accession": ["S1", "S2", "S3"], **{f"prob_{s}": [0.0] * 3 for s in ["inflow", "effluent", "sludge", "digester", "sewer"]}}).to_csv(preds, sep="\t", index=False)
    for labels in (["digester", "", "none"], ["digester", "sluge", "none"], ["digester", "none,sludge", "none"]):
        sheet = tmp_path / "sheet.tsv"
        pd.DataFrame({"item": [1, 2, 3], "accession": ["S1", "S2", "S3"], "labels": labels}).to_csv(sheet, sep="\t", index=False)
        result = CliRunner().invoke(labeling, ["score", "--sheet", str(sheet), "--key", str(preds)])
        assert result.exit_code != 0, labels
        assert "item 2" in result.output


def test_flow_wording_added_2026_10_14():
    import re

    from external_metadata_awareness.wastewater_subtype_classifier import INFLOW, OUTFLOW

    def has(pattern, text):
        return re.search(pattern, text, re.IGNORECASE) is not None

    assert has(INFLOW, "Incoming wastewater from a wastewater treatment plant")
    for text in ["effulent", "Waste water PDA Efluent C", "wastewater secondary effleunt", "Treated municipal sewage44",
                 "Train A, secondary treated water", "DNA extracted from after secondary treatment"]:
        assert has(OUTFLOW, text), text
    for text in ["heat treated municipal wastewater sludge", "untreated municipal sewage", "secondary sludge"]:
        assert not has(OUTFLOW, text), text
