"""Smoke tests for the console_scripts entry points (issue #470, tier 1).

These catch the most common dependency and refactor breakage without needing
MongoDB or network access:

- Every entry-point target must import and expose its referenced function.
  This catches dead entries (a renamed/deleted module) and any import-time
  breakage from a dependency bump.
- Every entry point must be a click command whose ``--help`` exits 0 (via
  click's CliRunner, which does not run the command body, so nothing connects
  or hangs). All console_scripts in this project use click; the test enforces
  that convention so a new argparse- or bare-``sys.argv``-based entry point
  fails here instead of silently diverging.
"""

import importlib
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

import click
import pytest
from click.testing import CliRunner

_PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def _load_scripts_config():
    try:
        raw = _PYPROJECT.read_text(encoding="utf-8")
    except OSError as exc:
        pytest.fail(f"Unable to read {_PYPROJECT}: {exc}", pytrace=False)

    try:
        data = tomllib.loads(raw)
    except tomllib.TOMLDecodeError as exc:
        pytest.fail(f"Unable to parse TOML in {_PYPROJECT}: {exc}", pytrace=False)

    try:
        poetry_cfg = data["tool"]["poetry"]
    except (KeyError, TypeError) as exc:
        pytest.fail(
            f"{_PYPROJECT} is missing expected [tool.poetry] structure: {exc}",
            pytrace=False,
        )

    if not isinstance(poetry_cfg, dict):
        pytest.fail(
            f"{_PYPROJECT} has invalid [tool.poetry] value; expected a table/dict.",
            pytrace=False,
        )

    scripts = poetry_cfg.get("scripts", {})

    if not isinstance(scripts, dict):
        pytest.fail(
            f"{_PYPROJECT} has invalid [tool.poetry.scripts] value; expected a table/dict.",
            pytrace=False,
        )
    return scripts


_SCRIPTS = _load_scripts_config()
_ENTRY_POINTS = sorted(_SCRIPTS.items())
_IDS = [name for name, _ in _ENTRY_POINTS]


@pytest.mark.parametrize("name,target", _ENTRY_POINTS, ids=_IDS)
def test_entry_point_loads(name, target):
    """The target module imports and the referenced function exists."""
    module_path, _, func_name = target.partition(":")
    module = importlib.import_module(module_path)
    assert hasattr(module, func_name), f"{module_path} has no attribute {func_name!r}"


@pytest.mark.parametrize("name,target", _ENTRY_POINTS, ids=_IDS)
def test_click_entry_point_help(name, target):
    """Every entry point is a click command whose --help exits 0."""
    module_path, _, func_name = target.partition(":")
    obj = getattr(importlib.import_module(module_path), func_name)
    assert isinstance(obj, click.BaseCommand), (
        f"{name} ({target}) is not a click command; all console_scripts in this "
        "project use click."
    )
    result = CliRunner().invoke(obj, ["--help"])
    assert result.exit_code == 0, f"{name} --help exited {result.exit_code}:\n{result.output}"


@pytest.mark.parametrize("name,target", _ENTRY_POINTS, ids=_IDS)
def test_non_click_entry_point_invokes(name, target, monkeypatch):
    """Non-click entry points are callable and can be invoked in a smoke mode."""
    module_path, _, func_name = target.partition(":")
    obj = getattr(importlib.import_module(module_path), func_name)
    if isinstance(obj, click.BaseCommand):
        pytest.skip(f"{name} is a click command")

    assert callable(obj), f"{name} entry point target is not callable"
    monkeypatch.setattr(sys, "argv", [name, "--help"])

    try:
        obj()
    except SystemExit as exc:
        assert exc.code in (0, None), f"{name} exited with non-zero code: {exc.code}"
