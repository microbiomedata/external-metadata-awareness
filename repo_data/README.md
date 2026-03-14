# repo_data

## Purpose

`repo_data/` is now a structural directory for repo-cataloging metadata, not a checked-in cache of GitHub snapshots.

It is useful for:

- documenting intended monitoring tiers for future regeneration
- keeping repo-cataloging guidance close to the regeneration notes
- making future cleanup and rebuild work explicit

It is **not** the authority on which GitHub orgs Mark should monitor.

## Monitoring Authority

Monitoring priority is defined by an external operator-maintained monitoring document outside this repo.

That document answers:

- which orgs should be monitored by default
- which orgs are secondary / opportunistic
- which colleagues are active outside the default set

This directory should support that document, not compete with it.

## How To Use This Directory

The machine-readable owner catalog lives in:

- `repo_data/catalog.yaml`

That file describes intended owner tiers for future re-fetch work. The repo no longer keeps the generated owner snapshot trees under version control.

### Category meanings

`default_monitoring`
- first-class monitoring owners that align to the authoritative doc

`spillover_org`
- org-level caches outside the default set that still matter because colleagues work there

`person_or_small_scope_cache`
- narrow caches that are useful as support, but should not drive monitoring priority

`broad_historical_crawl`
- high-breadth historical caches that are valuable for exploration but not priority-setting

## Non-Goals

This README does **not** imply:

- deletion of local clones
- removal of notes about these orgs
- that generated repo snapshots belong in git

## Practical Rule

When deciding whether an org deserves active attention:

1. Start with the authoritative monitoring doc.
2. Use `repo_data/catalog.yaml` to decide which owners belong in a regenerated local cache.
3. Regenerate snapshots locally when repo-level detail is actually needed.
4. If an org appears only here and not in the authoritative doc, do not treat it as a monitoring priority without new evidence.
