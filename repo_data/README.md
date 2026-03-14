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

### Active monitoring folders

These align directly with the current default monitoring set and are the first folders to consult when deeper repo-level detail is needed:

- `berkeleybop`
- `linkml`
- `monarch-initiative`
- `microbiomedata`
- `Knowledge-Graph-Hub`
- `CultureBotAI`
- `ai4curation`
- `biolink`
- `INCATools`
- `GenomicsStandardsConsortium`
- `EnvironmentOntology`
- `contextualizer-ai`

### Secondary spillover folders

These are useful when the authoritative doc indicates colleague activity outside the default monitoring set:

- `OBOAcademy`
- `OBOFoundry`
- `oborel`
- `perma-id`
- `ber-data`
- `EBISPOT`

### Broad historical crawls

These folders contain useful historical breadth, but should not be used to decide monitoring priority:

- `cmungall`
- `turbomam`
- `mcwdsi`

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
