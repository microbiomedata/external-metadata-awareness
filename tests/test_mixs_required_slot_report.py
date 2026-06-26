from pathlib import Path

import pytest
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError

from external_metadata_awareness import mixs_required_slot_report as report


def test_is_nmdc_supported_class_combination_and_other_are_unsupported():
    assert report.is_nmdc_supported_class("MigsBaSoil", "combination", {}) is False
    assert report.is_nmdc_supported_class("SomeClass", "other", {}) is False
    assert report.is_nmdc_supported_class("SomeClass", "unknown", {}) is False


def test_connect_mongo_injects_credentials_when_uri_lacks_credentials(
    monkeypatch, tmp_path: Path
):
    env_file = tmp_path / ".env"
    env_file.write_text("MONGO_USER=test-user\nMONGO_PASSWORD=test-pass\n")
    captured: dict[str, str] = {}

    class FakeAdmin:
        def command(self, command_name: str):
            assert command_name == "ping"
            return {"ok": 1}

    class FakeClient:
        def __init__(self, uri: str, serverSelectionTimeoutMS: int):
            captured["uri"] = uri
            captured["timeout"] = str(serverSelectionTimeoutMS)
            self.admin = FakeAdmin()

    monkeypatch.setattr(report, "MongoClient", FakeClient)
    # appName includes an '@' in the query string to ensure URI parsing does not
    # mistake query text for inline credentials.
    report.connect_mongo(
        "mongodb://localhost:27017/nmdc?appName=user@example.com", str(env_file)
    )

    assert "test-user:test-pass@" in captured["uri"]
    assert captured["timeout"] == "8000"


def test_connect_mongo_replaces_partial_inline_credentials(monkeypatch, tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("MONGO_USER=test-user\nMONGO_PASSWORD=test-pass\n")
    captured: dict[str, str] = {}

    class FakeAdmin:
        def command(self, command_name: str):
            assert command_name == "ping"
            return {"ok": 1}

    class FakeClient:
        def __init__(self, uri: str, serverSelectionTimeoutMS: int):
            captured["uri"] = uri
            captured["timeout"] = str(serverSelectionTimeoutMS)
            self.admin = FakeAdmin()

    monkeypatch.setattr(report, "MongoClient", FakeClient)
    report.connect_mongo("mongodb://useronly@localhost:27017/nmdc", str(env_file))

    assert "useronly@" not in captured["uri"]
    assert "@localhost:27017/nmdc" in captured["uri"]
    assert captured["timeout"] == "8000"


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (
            OperationFailure("auth failed"),
            "MongoDB authentication/authorization failed.",
        ),
        (
            ConnectionFailure("network down"),
            "Could not reach MongoDB server.",
        ),
        (PyMongoError("generic"), "MongoDB client error: generic"),
    ],
)
def test_connect_mongo_wraps_ping_exceptions(monkeypatch, error, expected):
    class FakeAdmin:
        def command(self, command_name: str):
            raise error

    class FakeClient:
        def __init__(self, _uri: str, **_kwargs):
            self.admin = FakeAdmin()

    monkeypatch.setattr(report, "MongoClient", FakeClient)

    with pytest.raises(report.click.ClickException, match=expected):
        report.connect_mongo("mongodb://localhost:27017/nmdc", None)


def test_fetch_env_package_weights_uses_shared_pipeline(monkeypatch):
    class FakeCollection:
        def aggregate(self, pipeline):
            assert pipeline == report.ENV_PACKAGE_WEIGHT_PIPELINE
            return [{"_id": "soil", "n": 3}]

    class FakeDatabase:
        def __getitem__(self, name: str):
            assert name == "biosample_set"
            return FakeCollection()

    class FakeClient:
        def get_default_database(self):
            return FakeDatabase()

    monkeypatch.setattr(report, "connect_mongo", lambda *_args, **_kwargs: FakeClient())

    counts = report.fetch_env_package_weights("mongodb://localhost:27017/nmdc", None)

    assert counts["Soil"] == 3


def test_load_annotations_raises_for_missing_required_columns(tmp_path: Path):
    annotations = tmp_path / "annotations.tsv"
    annotations.write_text("slot\tpriority\nfoo\tP0\n")

    with pytest.raises(ValueError, match="missing required columns: comment"):
        report.load_annotations(annotations)
