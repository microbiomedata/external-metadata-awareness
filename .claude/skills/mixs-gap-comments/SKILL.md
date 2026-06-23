---
name: mixs-gap-comments
description: >-
  Annotate the MIxS checklist/extension slot report with grounded priority and
  comment columns judging how important it is for NMDC to add each missing MIxS
  slot. Use when asked to assess MIxS slot gaps, prioritize slots to add to
  nmdc-schema, or produce the report Alicia Clum requested. Builds on the
  mixs-required-slot-report tool.
---

# MIxS gap comments

Produce a prioritized, commented version of the MIxS required-slot report. The
mechanical report (`mixs-required-slot-report`, see
`docs/mixs-required-slot-report.md`) says *which* MIxS checklist/extension slots
are required/recommended and whether they already have an NMDC home. This skill
adds the editorial layer: for each gap slot, **how important is it for NMDC to
add, and does NMDC already capture the concept another way?**

## Inputs that ground the judgment

Do not invent importance. Each comment rests on three verifiable inputs:

1. **Source class + relevance weight.** The report's `class_type`,
   `nmdc_supported`, and `nmdc_relevance_weight` columns. The weight is the
   share of biosamples in that environment for the chosen `--weight-source`:
   `env-package` (realized prod `biosample_set.env_package`, the default;
   Soil dominates, then Water) or `submission-rows` (submission portal). The
   baked snapshots live in `EXTENSION_WEIGHT_SNAPSHOTS` in the tool. A slot
   required only in an out-of-scope extension (food, human, symbiont,
   agriculture) is low priority by mission.
2. **Mission alignment.** NMDC is an environmental-microbiome resource. In-scope
   checklists for this report are `Mims` and `MigsBa` (Alicia Clum's
   2026-06-18 scope). The genome/marker checklists (Mimag, Miuvig, Mimarks*,
   Migs{Eu,Pl,Vi,Org}) and non-environmental extensions are out of mission
   unless the user widens scope.

   **Recency overlay.** Historical counts miss active work. The report's
   `nmdc_active_work` / `nmdc_active_work_note` columns
   (`NMDC_ACTIVE_WORK_BOOST` in the tool) flag classes under current
   development whose future volume the weights do not capture, e.g. `MigsBa` is
   boosted because JGI isolate modeling (issue #2803) will export isolates to
   NCBI as MIGS-BA. Treat an active-work flag as an upweight in step 5, even
   when the usage weight is low or absent. Keep these entries dated and
   issue-linked; revisit as work lands.
3. **Existing NMDC mechanism.** Whether the concept is already captured, even
   under a different slot name or modeling pattern. **This is the input that
   must be verified, never guessed** (see the
   `feedback-verify-slot-coverage-claims` memory). Read the MIxS slot's real
   `description` and `range`, then look in the NMDC schema for a native slot or
   process class that captures the same concept, and read *its* definition
   before claiming coverage.

## Procedure

1. **Run the mechanical report** (no annotations yet):

   ```bash
   mixs-required-slot-report -o local/mixs_required_slot_report.tsv
   ```

2. **Pick the slots to comment on.** Default scope: distinct slots that are
   `required=true` and `in_nmdc_schema=false` on at least one row where
   `nmdc_supported=true`. Widen to recommended slots or out-of-scope classes
   only if asked.

   ```bash
   awk -F'\t' 'NR>1 && $3=="true" && $9=="true" && $11=="false"{print $8}' \
       local/mixs_required_slot_report.tsv | sort -u
   ```
   (Columns: 3=nmdc_supported, 8=slot, 9=required, 11=in_nmdc_schema. Always
   confirm positions against the header, which changes as columns are added.)

3. **For each candidate slot, gather evidence before writing anything.** This
   repo has no `src/schema`; read definitions with `SchemaView` against the
   schemas the tool uses (or a local nmdc-schema clone, if present):

   ```python
   from linkml_runtime import SchemaView
   from external_metadata_awareness.mixs_required_slot_report import (
       DEFAULT_MIXS_SCHEMA, DEFAULT_NMDC_SCHEMA,
   )
   mixs = SchemaView(DEFAULT_MIXS_SCHEMA)
   nmdc = SchemaView(DEFAULT_NMDC_SCHEMA)
   slot = mixs.get_slot("num_replicons")          # MIxS range + description
   # candidate NMDC mechanism: scan nmdc.all_slots() / nmdc.get_slot(name)
   # and read the candidate's .range and .description before claiming coverage.
   ```
   Also note which in-scope classes require the slot and their weights (from the
   report). Confirm the concept matches; do not match on slot name alone.

4. **Grade the coverage claim** as one of:
   - `not-covered` - no NMDC slot or pattern captures the concept.
   - `uncertain-mapping` - a candidate native slot exists but differs in range
     or semantics (present as "candidate overlap to confirm with the team").
   - `firm-covered` - verified same concept, different name/shape.

5. **Assign priority** from weight x scope x coverage, with the recency overlay:
   - `high` - required in a high-weight in-scope environment, or in a class
     flagged `nmdc_active_work` (e.g. MigsBa), not-covered, no firm alternative.
   - `medium` - lower-weight in-scope environment, or uncertain-mapping, or a
     plausible alternative mechanism needs confirmation.
   - `low` - out-of-scope class, recommended-only, or firm-covered elsewhere.
   An active-work flag upgrades priority one step even if the usage weight is
   low; say so in the comment.

6. **Write the annotations TSV** (`local/mixs_gap_annotations.tsv`), one row per
   slot, header `slot<TAB>priority<TAB>comment`. Start from the committed seed
   `mixs_gap_annotations.seed.tsv` next to this file. Keep comments to one or two
   sentences that name the source class(es) + weight, the mission read, and the
   graded coverage finding. No em dashes; plain language.

7. **Merge and emit the final report:**

   ```bash
   mixs-required-slot-report \
       --annotations local/mixs_gap_annotations.tsv \
       -o local/mixs_required_slot_report_annotated.tsv
   ```

   Or use the Makefile target `make mixs-required-slot-report-annotated`.

## Output discipline

- The annotation is keyed by slot, so it applies to every class row for that
  slot. If a slot's priority genuinely differs by class (e.g. required in Soil
  but optional elsewhere), say so in the comment rather than splitting rows.
- Annotate only the in-scope gap slots by default; leave the rest blank.
- Comments are read by colleagues who flag AI-generated text. State the source
  class, weight, and coverage grade plainly. Never assert coverage you did not
  verify against the native slot's definition.
- `local/` is gitignored scratch; this skill writes there and does not touch
  committed files.
