"""Tests for BioSample accession lookup in the efetch adhoc script (no network)."""

import click
import pytest

from external_metadata_awareness.adhoc import dict_print_biosamples_from_efetch as script


class FakeResponse:
    def __init__(self, idlist):
        self.idlist = idlist

    def raise_for_status(self):
        pass

    def json(self):
        return {"esearchresult": {"idlist": self.idlist}}


def fake_get(idlist, calls):
    def get(url, params):
        calls.append((url, params))
        return FakeResponse(idlist)
    return get


@pytest.fixture(autouse=True)
def no_wait(monkeypatch):
    monkeypatch.setattr(script, "REQUEST_INTERVAL_SECONDS", 0)


def test_accession_is_resolved_with_esearch_accn(monkeypatch):
    calls = []
    monkeypatch.setattr(script.requests, "get", fake_get(["37939948"], calls))
    assert script.resolve_biosample_uid("SAMEA10021844") == "37939948"
    url, params = calls[0]
    assert url.endswith("esearch.fcgi")
    assert params["term"] == "SAMEA10021844[accn]"


@pytest.mark.parametrize("idlist", [[], ["1", "2"]])
def test_accession_matching_zero_or_several_uids_fails(monkeypatch, idlist):
    monkeypatch.setattr(script.requests, "get", fake_get(idlist, []))
    with pytest.raises(click.ClickException):
        script.resolve_biosample_uid("SAMEA19359001")
