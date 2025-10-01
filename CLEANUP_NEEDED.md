# Repository Cleanup Assessment

## Newly Created Holding Areas (Need Review)

### `claude-mds/`
Claude-generated documentation and analysis files. Need to assess:
- Which are still relevant/accurate vs outdated
- What should move to proper documentation locations
- What can be archived or deleted
- Examples: env-triad-annotation.md, makefile-analysis.md, gold-knowledge-management.md

### `unorganized/`
Miscellaneous files moved from other locations. Needs full audit.

## Questionable Directories (Assess Utility)

### `external_metadata_awareness/adhoc/`
One-off scripts, 8 files:
- **Decision needed**: Are these still useful? Should they be:
  - Moved to a `scripts/adhoc/` or `scripts/exploratory/`?
  - Documented and kept?
  - Deleted if superseded?
- Examples: `cborg_test.py`, `dict_print_biosamples_from_efetch.py`, `infer_first_committer.py`

### `mongo-js/has_python_implementation/`
MongoDB scripts with Python equivalents (2 files):
- **Question**: If Python implementations exist and are preferred, delete these?
- Or keep as reference/alternative implementations?

### `mongo-js/prints_does_not_insert/`
Read-only MongoDB scripts (2 files):
- **Question**: Are these utility scripts still used?
- Should they be in a `scripts/` or `tools/` directory instead?

## Areas Needing Documentation Assessment

### `lexmatch-shell-scripts/`
3 shell scripts total.
- **Questions**:
  - What is lexmatch? (appears to be lexical matching for ontology terms)
  - How would we recreate if necessary?
  - What is it good for?
  - Is it still actively used?
  - Should usage be documented in CLAUDE.md?

### `notebooks/`
Multiple subdirectories including:
- `mixs-slot-ranking`
- `mixs_inline_examples_checking`
- `multi-lexmatch`
- `software_methods_exploration`
- `mixs_preferred_unts`
- `old/` (likely candidates for deletion)
- `github-repo-metadata`

**Questions**:
- Which notebooks are current/active vs exploratory/obsolete?
- What is "metpo" related work? (mentioned in prompt)
- Should there be a notebooks/README.md explaining organization?
- Should `notebooks/old/` be archived or deleted?

## Recommended Next Steps

1. **Triage Session 1: claude-mds/**
   - Review each file's relevance
   - Move keepers to appropriate docs locations
   - Delete outdated analysis

2. **Triage Session 2: Scripts**
   - `adhoc/` - keep, move, or delete?
   - `mongo-js/has_python_implementation/` - redundant?
   - `mongo-js/prints_does_not_insert/` - still useful?

3. **Documentation Session: Active Tools**
   - Document lexmatch purpose and usage
   - Document notebook organization and purpose
   - Add to CLAUDE.md if user-facing

4. **Archive Session: Old Work**
   - `notebooks/old/` review
   - `unorganized/` triage
   - Consider creating `archive/` for historical but non-active work

## Notes
- Don't want to lose good documentation or tools
- Some stuff likely outdated and can be removed
- This is for future cleanup - documented but not blocking current work
