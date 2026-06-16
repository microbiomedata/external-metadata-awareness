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
import tomllib
from pathlib import Path

import click
import pytest
from click.testing import CliRunner

_PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"
_SCRIPTS = tomllib.loads(_PYPROJECT.read_text())["tool"]["poetry"].get("scripts", {})
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
