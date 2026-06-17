"""Smoke tests for the console_scripts entry points (issue #470, tier 1).

These catch the most common dependency and refactor breakage without needing
MongoDB or network access:

- Every entry-point target must import and expose its referenced function.
  This catches dead entries (a renamed/deleted module) and any import-time
  breakage from a dependency bump.
- For click-based entry points, ``--help`` must exit 0 (via click's CliRunner,
  which does not run the command body, so nothing connects or hangs).

Entry points that are not click commands (e.g. argparse-based) are still
covered by the load test; their ``--help`` is just not exercised here.
"""

import importlib
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
    except Exception as exc:
        pytest.fail(f"Unable to parse TOML in {_PYPROJECT}: {exc}", pytrace=False)

    try:
        scripts = data["tool"]["poetry"].get("scripts", {})
    except (KeyError, TypeError) as exc:
        pytest.fail(
            f"{_PYPROJECT} is missing expected [tool.poetry] structure: {exc}",
            pytrace=False,
        )

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
    """click-based entry points respond to --help with exit code 0."""
    module_path, _, func_name = target.partition(":")
    obj = getattr(importlib.import_module(module_path), func_name)
    if not isinstance(obj, click.BaseCommand):
        pytest.skip(f"{name} is not a click command")
    result = CliRunner().invoke(obj, ["--help"])
    assert result.exit_code == 0, f"{name} --help exited {result.exit_code}:\n{result.output}"
