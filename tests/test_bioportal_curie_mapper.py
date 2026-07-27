"""Unit tests for BioPortal LOOM mapping selection.

fetch_mappings ends in a bare `except Exception: return []`, so anything that
raises mid-loop discards every mapping for the source term rather than just
the offending entry. These tests cover that boundary.
"""

import types

import pytest

from external_metadata_awareness import new_bioportal_curie_mapper as mapper

_SOURCE_ID = "http://purl.obolibrary.org/obo/ENVO_00000001"
_GOOD_ID = "http://purl.obolibrary.org/obo/DOID_1234"


def _class(class_id, ontology, self_link="https://example.invalid/self"):
    entry = {"links": {"ontology": ontology, "self": self_link}}
    if class_id is not None:
        entry["@id"] = class_id
    return entry


@pytest.fixture
def stub_bioportal(monkeypatch):
    """Serve a canned mappings payload and a canned mapped-term lookup."""

    def _install(payload):
        def fake_get(url, headers=None, timeout=None):
            return types.SimpleNamespace(
                status_code=200,
                raise_for_status=lambda: None,
                json=lambda: payload,
            )

        monkeypatch.setattr(mapper.requests, "get", fake_get)
        monkeypatch.setattr(
            mapper,
            "get_mapped_term_info",
            lambda self_link, api_key: {"prefLabel": "example label", "obsolete": False},
        )

    return _install


def test_candidate_without_id_does_not_discard_the_other_mappings(stub_bioportal):
    """A class missing @id must be skipped, not take down the whole result.

    It previously reached converter.compress(target_cls["@id"]), raised
    KeyError, and the outer handler returned [] for the source term.
    """
    stub_bioportal([
        {
            "source": "LOOM",
            "classes": [
                _class(_SOURCE_ID, "https://data.bioontology.org/ontologies/ENVO"),
                _class(None, "https://data.bioontology.org/ontologies/DOID"),
                _class(_GOOD_ID, "https://data.bioontology.org/ontologies/DOID"),
            ],
        }
    ])

    result = mapper.fetch_mappings("https://example.invalid/mappings", "key", _SOURCE_ID)

    assert [m["curie"] for m in result] == ["DOID:1234"]


def test_non_string_id_is_skipped(stub_bioportal):
    """@id present but not a string is equally unusable."""
    bad = _class(None, "https://data.bioontology.org/ontologies/DOID")
    bad["@id"] = 12345
    stub_bioportal([
        {
            "source": "LOOM",
            "classes": [
                _class(_SOURCE_ID, "https://data.bioontology.org/ontologies/ENVO"),
                bad,
                _class(_GOOD_ID, "https://data.bioontology.org/ontologies/DOID"),
            ],
        }
    ])

    result = mapper.fetch_mappings("https://example.invalid/mappings", "key", _SOURCE_ID)

    assert [m["curie"] for m in result] == ["DOID:1234"]


def test_well_formed_payload_still_maps(stub_bioportal):
    """Guard against the filter rejecting valid candidates."""
    stub_bioportal([
        {
            "source": "LOOM",
            "classes": [
                _class(_SOURCE_ID, "https://data.bioontology.org/ontologies/ENVO"),
                _class(_GOOD_ID, "https://data.bioontology.org/ontologies/DOID"),
            ],
        }
    ])

    result = mapper.fetch_mappings("https://example.invalid/mappings", "key", _SOURCE_ID)

    assert [m["curie"] for m in result] == ["DOID:1234"]


def test_non_loom_sources_are_ignored(stub_bioportal):
    stub_bioportal([
        {
            "source": "CUI",
            "classes": [
                _class(_SOURCE_ID, "https://data.bioontology.org/ontologies/ENVO"),
                _class(_GOOD_ID, "https://data.bioontology.org/ontologies/DOID"),
            ],
        }
    ])

    result = mapper.fetch_mappings("https://example.invalid/mappings", "key", _SOURCE_ID)

    assert result == []
