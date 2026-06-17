"""Notebook syntax smoke test (#470 tier 2).

Every notebook's code cells must be syntactically valid Python. This does NOT
execute notebooks (they need MongoDB / data / network); it parses each .ipynb as
JSON and ast-parses the code cells, so it catches half-edited or broken
notebooks and syntax errors introduced by bulk edits, with no external services.

IPython line magics (`%`, `!`, `?`) are blanked and whole cell-magic cells
(`%%bash`, `%%time`, ...) are skipped, since those are not plain Python.
Top-level `await` is allowed (valid in notebooks).
"""

import ast
import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent
_NOTEBOOKS = sorted((_REPO / "notebooks").rglob("*.ipynb"))
_IDS = [str(p.relative_to(_REPO)) for p in _NOTEBOOKS]


def _is_cell_magic(src: str) -> bool:
    for line in src.splitlines():
        if line.strip():
            return line.lstrip().startswith("%%")
    return False


def _strip_line_magics(src: str) -> str:
    return "\n".join(
        "" if line.lstrip().startswith(("%", "!", "?")) else line
        for line in src.splitlines()
    )


@pytest.mark.parametrize("nb_path", _NOTEBOOKS, ids=_IDS)
def test_notebook_code_cells_parse(nb_path):
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        if _is_cell_magic(src):
            continue
        code = _strip_line_magics(src)
        try:
            compile(
                code,
                f"{nb_path.name}#cell{i}",
                "exec",
                flags=ast.PyCF_ONLY_AST | ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
        except SyntaxError as e:  # noqa: PERF203
            pytest.fail(f"{nb_path.relative_to(_REPO)} code cell {i}: {e}")
