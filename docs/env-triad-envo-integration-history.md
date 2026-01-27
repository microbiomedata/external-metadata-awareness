# Environmental Triad: ENVO Subset Integration History

This document provides historical context for [ADR-0015](https://github.com/microbiomedata/issues/blob/main/decisions/0015-env-triad-value-sets.md), which documents NMDC's decision to discontinue ENVO subset integration.

## Background: ENVO Subset Integration Attempt

From August 2024 through August 2025, NMDC attempted to publish value sets by injecting `oboInOwl:inSubset` annotations into ENVO via ROBOT templates. This would have enabled tools like OLS/BioPortal to query NMDC subsets directly from ENVO releases.

### Implementation Details

- Created ROBOT template (`nmdc_env_context_subset_membership.tsv`) mapping ENVO terms to NMDC subset IDs
- Defined subset annotation properties in ENVO: `ENVO:03605010` (NMDC environmental context subsets) and its sub-properties
- Integrated into ENVO Makefile build process

### Why ENVO Integration Was Abandoned

1. **Technical fragility**: The Aug 2025 ENVO release (v2025-08-19) accidentally dropped all NMDC subset annotations. The multi-step ODK build process has many failure points with silent failures (build succeeds even when annotations are missing).

2. **Architectural limitation (fundamental)**: NMDC value sets contain terms from multiple ontologies:
   - ENVO terms (environmental contexts)
   - PO terms (plant anatomical structures for plant-associated samples)
   - UBERON terms (animal anatomical structures for host-associated samples)

   ENVO can only annotate ENVO terms. Publishing complete NMDC value sets via ENVO subsets is architecturally impossible without coordinating with PO and UBERON maintainers to import NMDC subset definitions into each ontology.

3. **Release coupling**: NMDC value set updates required waiting for ENVO releases, introducing delays and coordination overhead.

---

## Note on "Cherry-Picking" Principle

The original ADR (Aug 2024) established a "no cherry-picking" principle ([#844](https://github.com/microbiomedata/issues/issues/844)): specific terms should not be individually removed; elimination must always be done via general query changes.

This principle was relaxed because no purely query-based approach produced usable value sets. The voting workflow effectively cherry-picks terms, but does so through systematic, reproducible curation with documented rationale (vote sums, expert consensus).

---

## Enumeration Naming Pattern

Value set enumerations follow this pattern:

```
Env[Scale][Extension]Enum
```

Examples: `EnvBroadScaleSoilEnum`, `EnvLocalScaleWaterEnum`, `EnvMediumPlantAssociatedEnum`

### Currently Implemented Extensions

Soil, Water, Sediment, Plant-associated (12 enumerations total: 4 extensions × 3 slots)

Additional MIxS extensions do not yet have curated value sets. See [#79](https://github.com/microbiomedata/issues/issues/79) for planned expansion.

---

## Note on Current Vote Processing

The existing 12 value sets were created using one-off Jupyter notebooks with varied approaches. In some cases (e.g., soil env_medium, soil env_broad_scale), the ontology structure was sufficient for query-only selection without expert voting. Future iterations should standardize vote processing where voting is used. See the [lifecycle document](environmental-triad-value-set-lifecycle.md) for details.

---

## Action Items

### Completed

- [x] Implement LinkML enumerations for 4 extensions × 3 slots (12 enums) in submission-schema
- [x] Establish voting workflow with Google Sheets
- [x] Document workflow in external-metadata-awareness

### Proposed

1. **Request ENVO deprecate NMDC subset annotation properties**

   Request deprecation of `ENVO:03605010` (NMDC environmental context subsets) and all its sub-properties, as NMDC will no longer maintain them.

2. **Archive ROBOT template generation code**

   The `create_env_context_robot_template.py` script in submission-schema should be archived or removed, with documentation noting it represents a deprecated approach.

3. **Improve value set accessibility** (Issues #1351, #1352, #1353, submission-schema#392)
   - Add TSV/YAML download buttons to enumeration documentation pages
   - Fix NmdcEnvTriadEnums index page to properly organize and link enumerations
   - Improve navigation between grouping pages and individual enumeration pages
   - Configure w3id.org namespace for submission-schema persistent URLs

---

## Related Issues and Discussions

### microbiomedata/issues
- [#846](https://github.com/microbiomedata/issues/issues/846) - Document policies for each env triad term v2
- [#844](https://github.com/microbiomedata/issues/issues/844) - Evaluate OAK success for SOIL curated terms
- [#1138](https://github.com/microbiomedata/issues/issues/1138) - Add sediment PVs to ENVO subsets
- [#1351](https://github.com/microbiomedata/issues/issues/1351) - Create summarizing doc page
- [#1352](https://github.com/microbiomedata/issues/issues/1352) - Add TSV download buttons
- [#1353](https://github.com/microbiomedata/issues/issues/1353) - Configure w3id.org redirects
- [#1354](https://github.com/microbiomedata/issues/issues/1354) - Work with Pier to get PO/UBERON terms to ENVO (closed - no longer pursuing)
- [#502](https://github.com/microbiomedata/issues/issues/502) - Milestone: Harmonizing environmental science standards
- [#468](https://github.com/microbiomedata/issues/issues/468) - Milestone: Define EnvO value sets

### EnvironmentOntology/envo
- [#1642](https://github.com/EnvironmentOntology/envo/issues/1642) - NMDC value sets disappeared from 2025-08-19 release

### microbiomedata/submission-schema
- [#392](https://github.com/microbiomedata/submission-schema/issues/392) - w3id.org namespace configuration
