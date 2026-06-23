# MIxS required-slot gap report

Answers: which required MIxS checklist/extension slots has NMDC not given a
class home, and how important is each gap? It is built in two phases.

- **Phase 1 (deterministic):** a reproducible table from the schemas plus a
  weight source. Same inputs give the same table; no judgement.
- **Phase 2 (agentic):** an optional layer that adds `priority` and `comment`
  columns judging each gap. Produced by the `mixs-gap-comments` skill (or
  hand-authored) and merged back into the Phase 1 table.

Keep the phases separate: Phase 1 is auditable and re-runnable by anyone; Phase
2 is reviewable judgement that never changes the Phase 1 facts.

## Phase 1 — build the deterministic table

```bash
# Offline: uses a baked-in weight snapshot, no database needed.
mixs-required-slot-report -o local/mixs_required_slot_report.tsv

# Live weights from realized prod biosamples (default source), over the tunnel.
# See docs/nmdc-prod-mongo-tunnel.md to open the tunnel first.
mixs-required-slot-report --weight-source env-package --refresh-weights \
    --env-file local/.env -o local/mixs_required_slot_report.tsv
```

One `SchemaView` pass over the GSC MIxS schema keeps the checklist and extension
classes (combinations excluded) and, for each induced slot, emits these columns:

| column | meaning |
|---|---|
| `mixs_class`, `class_type` | the checklist or extension class |
| `nmdc_supported` | class is in NMDC's supported scope |
| `nmdc_relevance_weight`, `nmdc_biosample_count` | environment usage weight (from the chosen weight source) |
| `nmdc_active_work`, `nmdc_active_work_note` | recency overlay for classes under active work |
| `slot`, `required`, `recommended` | the induced slot and its MIxS requirement |
| `in_nmdc_schema`, `nmdc_class_count`, `nmdc_classes` | whether the slot has an NMDC home, and which classes carry it |

Weight sources (`--weight-source`): `env-package` (realized prod
`biosample_set.env_package`, the default) or `submission-rows` (submission
portal). Without `--refresh-weights` a baked snapshot is used so the table is
reproducible offline.

The in-scope gaps (supported, required, no NMDC home):

```bash
awk -F'\t' 'NR>1 && $3=="true" && $9=="true" && $11=="false"{print $8}' \
    local/mixs_required_slot_report.tsv | sort -u
```

## Phase 2 — add the agentic priority/comment columns

Phase 1 says *which* slots lack a home; Phase 2 judges *how important* each gap
is and whether NMDC already captures the concept another way. The judgement is
keyed by slot in an annotations TSV with the header `slot<TAB>priority<TAB>comment`.

Produce the annotations one of two ways:

1. **Skill (recommended):** run the `mixs-gap-comments` skill. It runs Phase 1,
   scopes to the gap slots, reads each MIxS slot definition, searches
   nmdc-schema for an existing mechanism, grades coverage
   (`not-covered` / `uncertain-mapping` / `firm-covered`) against the native
   slot's real definition, assigns `high`/`medium`/`low`, and writes the
   annotations TSV. See `.claude/skills/mixs-gap-comments/SKILL.md`.
2. **By hand:** edit a copy of the seed at
   `.claude/skills/mixs-gap-comments/mixs_gap_annotations.seed.tsv`.

Then merge the annotations back into the Phase 1 table; the `priority` and
`comment` columns appear only when `--annotations` is given:

```bash
mixs-required-slot-report \
    --annotations local/mixs_gap_annotations.tsv \
    -o local/mixs_required_slot_report_annotated.tsv
```

Coverage discipline: never assert a slot is covered from its name. Grade against
the native slot's actual range and definition, and present uncertain mappings as
candidates to confirm with the team, not as settled coverage.

## See also

- `docs/nmdc-prod-mongo-tunnel.md` — open the tunnel for `--refresh-weights`.
- `.claude/skills/mixs-gap-comments/SKILL.md` — the full Phase 2 procedure.

## Make targets

Both phases are wired as targets in `Makefiles/nmdc_metadata.Makefile`:

```bash
make mixs-required-slot-report            # Phase 1, offline baked weights
make mixs-required-slot-report-live       # Phase 1, live prod weights (tunnel up first)
make mixs-required-slot-report-annotated  # Phase 2, merge MIXS_GAP_ANNOTATIONS
```

Override `MIXS_REPORT_ENV_FILE` (prod credentials) or `MIXS_GAP_ANNOTATIONS`
(annotations path) as needed.
