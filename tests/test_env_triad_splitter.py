"""Unit tests for the pure env-triad value-splitting functions (#470 tier 4).

These functions parse free-text environmental-context values into components;
they take strings and return strings/dicts with no I/O, so they are cheap to
test and guard the core parsing logic against refactors.
"""

from external_metadata_awareness.new_env_triad_values_splitter import (
    extract_components,
    is_digits_only,
    make_plain_component,
    normalize_label,
)


def test_is_digits_only():
    assert is_digits_only("123") is True
    assert is_digits_only("12a") is False
    assert is_digits_only("") is False
    assert is_digits_only(None) is False


def test_normalize_label_lowercases_and_replaces_punctuation():
    assert normalize_label("Soil_Sample") == "soil sample"
    assert normalize_label("ENVO:00001  Foo") == "envo 00001 foo"


def test_make_plain_component():
    c = make_plain_component("ENVO soil")
    assert c["label"] == "envo soil"
    assert c["lingering_envo"] is True
    assert c["label_digits_only"] is False
    assert c["raw"] == "ENVO soil"


def test_extract_components_non_string_returns_empty():
    assert extract_components(123) == []


def test_extract_components_plain_token():
    comps = extract_components("soil")
    assert len(comps) == 1
    assert comps[0]["label"] == "soil"


def test_extract_components_bracketed_curie():
    comps = extract_components("soil [ENVO:00001]")
    assert len(comps) == 1
    assert comps[0]["prefix_uc"] == "ENVO"
    assert comps[0]["local"] == "00001"
    assert comps[0]["label"] == "soil"


def test_extract_components_splits_on_comma():
    comps = extract_components("soil, water")
    assert [c["label"] for c in comps] == ["soil", "water"]
