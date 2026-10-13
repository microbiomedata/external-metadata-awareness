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
