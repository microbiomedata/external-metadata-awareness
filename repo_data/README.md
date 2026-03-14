# repo_data

## Purpose

`repo_data/` is a local cache and evidence store for GitHub organization and repository snapshots.

It is useful for:

- repo-level lookup
- cached contributor summaries
- broad historical context
- supporting research on adjacent org ecosystems

It is **not** the authority on which GitHub orgs Mark should monitor.

## Monitoring Authority

Monitoring priority is defined outside this repo in:

- `/home/mark/bookmark-consolidation/bbop_orgs_to_monitor_authoritative.md`

That document answers:

- which orgs should be monitored by default
- which orgs are secondary / opportunistic
- which colleagues are active outside the default set

This directory should support that document, not compete with it.

## How To Use This Directory

The machine-readable owner catalog lives in:

- `repo_data/catalog.yaml`

That file categorizes every current top-level owner directory so future cleanup and re-fetch work can be done intentionally.

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

- deletion of cached org folders
- deletion of local clones
- removal of notes about these orgs
- a guarantee that every folder is current

## Practical Rule

When deciding whether an org deserves active attention:

1. Start with the authoritative monitoring doc.
2. If the org is in the default monitoring set, use `repo_data/<org>/` as supporting detail.
3. If the org is not in the default set but appears in the colleague spillover section, use `repo_data/` as secondary context.
4. If an org appears only here and not in the authoritative doc, do not treat it as a monitoring priority without new evidence.
