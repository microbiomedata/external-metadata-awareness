"""Unit tests for MongoDB connection URI resolution.

get_mongo_client(dry_run=True) builds the connection URI without opening a
connection, so the credential-injection logic can be tested without a server.
These guard two silent-failure bugs: credentials supplied via --env-file not
reaching the URI at all, and the dry-run path returning nothing usable.
"""

import logging
import subprocess
import types

import pytest
from click.testing import CliRunner

from external_metadata_awareness.mongodb_connection import get_mongo_client, main

_URI = "mongodb://localhost:27017/testdb"


@pytest.fixture(autouse=True)
def restore_root_logger():
    """Undo the CLI's logging.basicConfig(force=True) after each test.

    main() reconfigures the root logger by design, which would otherwise
    persist for the rest of the session and make test order matter.
    """
    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level
    try:
        yield
    finally:
        root.handlers[:] = saved_handlers
        root.setLevel(saved_level)


@pytest.fixture
def env_file(tmp_path, monkeypatch):
    """A .env file with credentials, isolated from any ambient MONGO_* vars."""
    for var in ("MONGO_USER", "MONGO_PASSWORD", "MONGO_AUTH_SOURCE"):
        monkeypatch.delenv(var, raising=False)
    path = tmp_path / ".env"
    path.write_text("MONGO_USER=testuser\nMONGO_PASSWORD=testpass\n")
    return str(path)


def test_dry_run_returns_connection_info_without_connecting():
    info = get_mongo_client(mongo_uri=_URI, dry_run=True)
    assert info["uri"] == _URI
    assert info["has_credentials"] is False


def test_env_file_credentials_are_injected_into_uri(env_file):
    """--env-file credentials must reach the URI; mongosh is handed this value."""
    info = get_mongo_client(mongo_uri=_URI, env_file=env_file, dry_run=True)
    assert info["has_credentials"] is True
    assert "testuser" in info["uri"]
    assert "/testdb" in info["uri"]


def test_env_file_credentials_add_auth_source(env_file):
    """Without authSource, auth is attempted against the URI's own database."""
    info = get_mongo_client(mongo_uri=_URI, env_file=env_file, dry_run=True)
    assert "authSource=admin" in info["uri"]


def test_existing_uri_credentials_are_replaced(env_file):
    info = get_mongo_client(
        mongo_uri="mongodb://olduser:oldpass@localhost:27017/testdb",
        env_file=env_file,
        dry_run=True,
    )
    assert "olduser" not in info["uri"]
    assert "testuser" in info["uri"]


def test_missing_env_file_is_an_error():
    with pytest.raises(ValueError, match="not found"):
        get_mongo_client(mongo_uri=_URI, env_file="/nonexistent/.env", dry_run=True)


def test_at_sign_in_option_value_is_not_read_as_credentials():
    """An "@" in an option value must not be reported as credentials.

    has_credentials used to be `"@" in uri`, which matches option values such
    as ?appName=user@example.com and claimed credentials that are not there.
    """
    info = get_mongo_client(
        mongo_uri="mongodb://localhost:27017/testdb?appName=user@example.com",
        dry_run=True,
    )
    assert info["has_credentials"] is False


def test_credentials_needing_escaping_raise_value_error(tmp_path, monkeypatch):
    """A password with reserved characters must surface as ValueError.

    Injecting it produces a URI that only fails when parsed. pymongo raises
    InvalidURI, which is not a ValueError, so it would skip the caller's
    URI-format error handling.
    """
    for var in ("MONGO_USER", "MONGO_PASSWORD", "MONGO_AUTH_SOURCE"):
        monkeypatch.delenv(var, raising=False)
    path = tmp_path / ".env"
    path.write_text("MONGO_USER=user\nMONGO_PASSWORD=p@ssw0rd\n")

    with pytest.raises(ValueError, match="after applying credentials"):
        get_mongo_client(mongo_uri=_URI, env_file=str(path), dry_run=True)


def test_cli_reports_uri_format_guidance_for_unescaped_credentials(tmp_path, monkeypatch):
    """The CLI keeps its URI-format guidance for that case."""
    for var in ("MONGO_USER", "MONGO_PASSWORD", "MONGO_AUTH_SOURCE"):
        monkeypatch.delenv(var, raising=False)
    path = tmp_path / ".env"
    path.write_text("MONGO_USER=user\nMONGO_PASSWORD=p@ssw0rd\n")

    result = CliRunner().invoke(main, ["--uri", _URI, "--env-file", str(path)])

    assert result.exit_code == 1
    assert "The MongoDB URI must use the format" in result.output


def test_verbose_wins_over_preconfigured_logging(env_file):
    """--verbose must work even when something already configured logging.

    logging.basicConfig is a no-op once handlers exist, so without force=True
    the flag silently does nothing under a test runner or any importer that
    configured logging first.
    """
    logging.basicConfig(level=logging.WARNING)

    result = CliRunner().invoke(main, ["--uri", _URI, "--env-file", env_file, "--verbose"])

    assert result.exit_code == 0, result.output
    assert logging.getLogger().level == logging.DEBUG


def test_dry_run_cli_reports_on_stdout(env_file):
    """The dry-run CLI must print something.

    It previously reported only through logger.debug, and nothing configures
    logging, so `mongo-connect --uri ...` produced no output at all.
    """
    result = CliRunner().invoke(main, ["--uri", _URI, "--env-file", env_file])

    assert result.exit_code == 0, result.output
    assert result.output.strip(), "dry-run CLI produced no output"
    assert "Credentials present in URI: yes" in result.output
    assert "testpass" not in result.output, "the URI must never be printed"


def test_mongosh_fallback_receives_env_file_credentials(env_file, monkeypatch):
    """The mongosh fallback must be handed the credential-injected URI.

    It previously passed the raw --uri straight through, so --env-file
    credentials never reached mongosh and auth failed even though the PyMongo
    client had connected fine. pymongo.MongoClient connects lazily, so no
    server is needed; only subprocess.run has to be stubbed out.
    """
    captured = {}

    def fake_run(cmd, *args, **kwargs):
        captured["cmd"] = cmd
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = CliRunner().invoke(
        main,
        [
            "--uri", _URI,
            "--env-file", env_file,
            "--command", "db.runCommand({ping: 1})",
        ],
    )

    assert result.exit_code == 0, result.output
    assert captured["cmd"][0] == "mongosh"
    mongosh_uri = captured["cmd"][1]
    assert "testuser" in mongosh_uri, "credentials from --env-file never reached mongosh"
    assert "authSource=" in mongosh_uri
    assert "/testdb" in mongosh_uri


@pytest.mark.parametrize(
    "bad_uri,message",
    [
        ("", "required"),
        ("http://localhost:27017/testdb", "must start with"),
        ("mongodb://localhost:27017", "database name"),
    ],
)
def test_invalid_uris_are_rejected(bad_uri, message):
    with pytest.raises(ValueError, match=message):
        get_mongo_client(mongo_uri=bad_uri, dry_run=True)
