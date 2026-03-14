# `repo_data` Regeneration

## Purpose

`repo_data/` is a local cache of GitHub repository metadata and README content for selected GitHub owners.

It is not the authority for "which orgs should I monitor?".
That authority should live in an external operator-maintained monitoring document, not in `repo_data/`.

This document explains the current reproducible path for rebuilding the existing `repo_data/` structure.

## Current Generator

The current on-disk `repo_data/` layout matches:

- [`unorganized/fetch_repos.sh`](/home/mark/gitrepos/external-metadata-awareness/unorganized/fetch_repos.sh)

This script generates, for each owner:

- one repo metadata file per repository: `repo_data/<owner>/<repo>.json`
- one README file per repository: `repo_data/<owner>/<repo>_README.md`
- one owner summary file: `repo_data/<owner>/_SUMMARY.json`

## Evidence This Is the Active Match

The script fetches and writes the same fields seen in current cache files:

- `name`
- `description`
- `createdAt`
- `updatedAt`
- `url`
- `defaultBranchRef`
- `firstCommitDate`
- `lastCommitDate`
- `topContributors` when `-c` is used

It also writes owner-level `_SUMMARY.json` files by aggregating `*.json` files in each owner directory.

That matches the current shape of files such as:

- [`repo_data/berkeleybop/berkeleybop.json`](/home/mark/gitrepos/external-metadata-awareness/repo_data/berkeleybop/berkeleybop.json)
- [`repo_data/berkeleybop/_SUMMARY.json`](/home/mark/gitrepos/external-metadata-awareness/repo_data/berkeleybop/_SUMMARY.json)

## Prerequisites

- `gh` CLI installed
- `jq` installed
- authenticated GitHub CLI session: `gh auth status`

The script exits early if those are missing.

## Regeneration Command

From the repository root:

```bash
bash unorganized/fetch_repos.sh \
  -d ./repo_data \
  -c \
  -o berkeleybop \
  -o linkml \
  -o monarch-initiative \
  -o microbiomedata \
  -o Knowledge-Graph-Hub \
  -o CultureBotAI \
  -o ai4curation \
  -o biolink \
  -o INCATools \
  -o GenomicsStandardsConsortium \
  -o EnvironmentOntology \
  -o contextualizer-ai
```

That command aligns with the current default monitoring set.

To include spillover or person-centric caches, add more `-o` flags for owners such as:

- `OBOAcademy`
- `OBOFoundry`
- `oborel`
- `perma-id`
- `EBISPOT`
- `cmungall`
- `mcwdsi`
- `turbomam`

## What the Script Actually Does

For each owner, the script:

1. Lists repositories with `gh repo list <owner> --limit 1000 --json name`
2. Fetches repo metadata with `gh repo view`
3. Fetches first and last commit dates with `gh api repos/<owner>/<repo>/commits`
4. Optionally fetches contributor counts with `gh api repos/<owner>/<repo>/contributors?per_page=10`
5. Fetches README content from `repos/<owner>/<repo>/readme`
6. Writes `_SUMMARY.json` from the per-repo JSON files

## Important Limitations

- This is a shell workflow, not yet a packaged Python or Makefile target.
- It depends on live GitHub API access and current `gh` auth state.
- `firstCommitDate` is inferred from a lightweight commits query and should be treated as a practical cache value, not audited provenance.
- `_SUMMARY.json` is derived from the local files present in an owner directory.
- There is no single manifest in the repo that declares which owners must be present in `repo_data/`.

## Related But Different GitHub Tooling

These are GitHub-related, but they do not regenerate the current `repo_data/` tree:

- [`Makefiles/github.Makefile`](/home/mark/gitrepos/external-metadata-awareness/Makefiles/github.Makefile)
  - fetches release notes, not repo cache snapshots
- [`notebooks/github-repo-metadata/sample_extraction_commands.sh`](/home/mark/gitrepos/external-metadata-awareness/notebooks/github-repo-metadata/sample_extraction_commands.sh)
  - extracts PR participants from saved JSON, not repo metadata trees
- [`external_metadata_awareness/adhoc/infer_first_committer.py`](/home/mark/gitrepos/external-metadata-awareness/external_metadata_awareness/adhoc/infer_first_committer.py)
  - a GitHub API utility, not the owner-cache generator

## Recommended Next Cleanup Step

If `repo_data/` is going to be kept long term, the next improvement should be to promote `unorganized/fetch_repos.sh` into a stable, documented entry point, for example:

- `scripts/fetch_repo_data.sh`
- or a Make target such as `make -f Makefiles/github.Makefile fetch-repo-data`

That would make future cleanup lower risk because the cache could be rebuilt intentionally rather than preserved by habit.
