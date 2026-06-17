# Removed adhoc scripts

Adhoc scripts deleted because each existed only to use a heavy dependency that
nothing else in the repo needed. Recoverable from git history
(`git log --all --diff-filter=D -- <path>`); both are small and easy to recreate.

## `cborg_test.py`
- **What it did:** a connectivity probe for the CBORG LLM gateway via the
  `openai` client (listed a few models, sent a test chat completion).
- **Why removed:** sole user of the `openai` dependency. Removed `openai` from
  the project (issue #467). To probe CBORG again, `pip install openai` and point
  an `OpenAI(base_url="https://api.cborg.lbl.gov")` client at it.
- **Removed in:** issue #467 (https://github.com/microbiomedata/external-metadata-awareness/issues/467).

## `infer_first_committer.py`
- **What it did:** inferred a GitHub repo's first committer using `pygithub`.
- **Why removed:** sole user of the `pygithub` dependency. Removed `pygithub`
  from the project (issue #467). The same is doable with the `gh` CLI
  (`gh api repos/<o>/<r>/commits`) or a plain `requests` call.
- **Removed in:** issue #467 (https://github.com/microbiomedata/external-metadata-awareness/issues/467).
