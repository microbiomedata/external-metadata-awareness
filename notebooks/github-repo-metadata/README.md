# github-repo-metadata/

Fetches GitHub issues, pull requests, and comments for a repository (currently
hardcoded to `microbiomedata/nmdc-metadata`) via the GitHub REST API. No script
in this repo does this — `external_metadata_awareness/fetch_github_releases.py`
fetches releases only.

- `fetch_github_issues_prs.ipynb` — pulls issues/PRs/comments to JSON.
- `sample_extraction_commands.sh` — the helper that split the JSON into the
  `*_title.txt` / `*_body.txt` / `*_created_at.txt` / `*_participants.txt` files.
- `github_issues_prs/` — committed output snapshot.

**Rerun when:** taking a fresh snapshot of a repo's issues/PRs. To target a
different repo, parametrize the hardcoded repo name (small change worth doing if
this is reused).
