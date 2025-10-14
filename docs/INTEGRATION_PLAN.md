# Documentation Integration & Verification Plan

**Created**: 2025-10-02
**Purpose**: Plan for verifying and consolidating documentation across the repository

---

## Phase 1: ARCHITECTURE.md Verification (IMMEDIATE)

### Issues Found
1. **MongoDB Collection Names**: ARCHITECTURE.md lists `biosample_harmonized_attributes` but actual collection is `biosamples_attributes`
2. **Missing Collections**: Actual collections not documented:
   - `attributes`
   - `biosamples_ids`, `biosamples_links`
   - `harmonized_name_dimensional_stats`, `harmonized_name_usage_stats`
   - `env_triad_component_labels` (not `triad_components_labels`)
   - `env_triad_component_curies_uc`
   - `biosamples_env_triad_value_counts_gt_1`
   - `global_nmdc_slots`, `global_mixs_slots`
   - `nmdc_range_slot_usage_report`
3. **Collection Purpose**: Need to verify purpose/usage for each collection

### Action Items
- [ ] Run mongosh queries to get actual collection stats
- [ ] Update ARCHITECTURE.md with correct collection names
- [ ] Document purpose for each collection
- [ ] Cross-reference with code that creates/uses these collections
- [ ] Add note about two biosample collections: `biosamples` (raw XML) and `biosamples_flattened` (normalized)

---

## Phase 2: Environmental Triad Value Set Workflow Documentation (HIGH PRIORITY)

### Current State
Content is **scattered** across multiple files:
- CLAUDE.md: High-level overview (85 lines, too much detail)
- `docs/nmdc-env-triad-valueset-lifecycle.md`: Comprehensive 299-line doc with full workflow
- `unorganized/README_environmental_context_value_sets.md`: submission-schema focused (59 lines)
- `notebooks/environmental_context_value_sets/voting-sheet-generation-readme.md`: Implementation details
- `docs/submission-schema-CLAUDE.md`: submission-schema repo documentation

### Recommended Structure

**Create**: `ENV_TRIAD_WORKFLOW.md` (authoritative, root directory)

**Content**:
1. **Quick Overview** (~50 lines)
   - What are environmental triads
   - Why they matter
   - Quick visual of the complete workflow

2. **Repository Responsibilities** (~100 lines)
   - external-metadata-awareness: Data extraction → Voting sheets
   - submission-schema: Vote processing → LinkML enumerations
   - envo: Ontology integration → inSubset annotations

3. **Complete Workflow** (~150 lines)
   - Stage 1-3: This repo (external-metadata-awareness)
   - Stage 4-6: submission-schema repo
   - Stage 7-8: envo repo
   - Cross-repo file paths and commands

4. **For More Detail** (~20 lines)
   - Link to detailed README in notebooks/environmental_context_value_sets/
   - Link to submission-schema documentation
   - Link to historical analysis in docs/

**Total**: ~320 lines (manageable, authoritative)

### Migration Strategy
1. **Keep in CLAUDE.md**: Only 15-20 lines pointing to ENV_TRIAD_WORKFLOW.md
2. **Move to ENV_TRIAD_WORKFLOW.md**: Consolidated content from all sources
3. **Update cross-links**: Ensure all docs point to new authoritative file
4. **Preserve historical**: Keep docs/ files intact with note they're superseded

---

## Phase 3: Cross-Repository Documentation Audit (MEDIUM PRIORITY)

### Repositories to Check
- [ ] **submission-schema**:
  - Location: `repo_data/microbiomedata/submission-schema_README.md`
  - Check for env triad workflow documentation
  - Verify file paths mentioned in workflows
  - Check for any contradictions with our docs

- [ ] **envo** (if cloned locally or via GitHub):
  - Verify ROBOT template paths
  - Confirm inSubset annotation process
  - Check Makefile targets

### Action Items
- [ ] Clone or fetch latest submission-schema
- [ ] Verify all file paths mentioned in nmdc-env-triad-valueset-lifecycle.md
- [ ] Document any changes to workflow since that doc was written
- [ ] Create cross-repo compatibility matrix

---

## Phase 4: Historical Documentation Consolidation (FUTURE)

See [Issue #224](https://github.com/microbiomedata/external-metadata-awareness/issues/224)

### Files to Review
- `docs/` (35+ files) - Keep for historical context
- `unorganized/` (50+ files) - Needs categorization
- Root directory MDs - Already handled (moved to phase 1 docs)

### Strategy
1. Create `docs/archive/` for superseded analysis
2. Keep `docs/` for session notes (useful for troubleshooting)
3. Move truly obsolete files to archive
4. Update README in each directory explaining status

---

## Implementation Order

### This Session (COMPLETED 2025-10-02)
1. ✅ Create this INTEGRATION_PLAN.md
2. ✅ Fix ARCHITECTURE.md MongoDB collections
3. ✅ Create ENV_TRIAD_WORKFLOW.md
4. ✅ Update CLAUDE.md to remove env triad details, add link

### Next Session
1. Cross-repository verification (submission-schema, envo)
2. Test all workflow steps end-to-end
3. Document any breaking changes or updates needed

### Future Session (Issue #224)
1. Historical documentation consolidation
2. Archive creation and organization
3. README updates for docs/ and unorganized/

---

## Success Criteria

### ARCHITECTURE.md
- [x] All MongoDB collection names match actual database
- [x] Each collection has documented purpose
- [x] Two biosample collections distinction documented
- [x] Collection categories organized (Core, Environmental, Supporting, etc.)
- [ ] Collection statistics are current (within 3 months) - DEFERRED
- [ ] Cross-references to code that creates/uses collections - DEFERRED

### ENV_TRIAD_WORKFLOW.md
- [x] Complete end-to-end workflow documented
- [x] All three repos covered (external-metadata-awareness, submission-schema, envo)
- [x] File paths verified and current
- [x] Clear handoff points between repos
- [x] MIxS integration explained
- [x] Quick start guide included
- [x] Common issues and solutions documented

### CLAUDE.md
- [x] Env triad section reduced to concise quick reference
- [x] Clear link to ENV_TRIAD_WORKFLOW.md in Quick Navigation
- [x] No duplication of detailed workflow content

---

## Notes

### Why This Matters
1. **Onboarding**: New contributors need clear, accurate documentation
2. **Cross-repo collaboration**: Teams working on submission-schema and envo need to understand our outputs
3. **Reproducibility**: Workflow must be documented to be repeatable
4. **Maintenance**: Scattered docs lead to inconsistencies and staleness

### Risks of Not Doing This
1. Workflow breaks when repo structures change
2. Domain knowledge exists only in Mark's head
3. Voting sheet generation becomes black box
4. submission-schema integration requires manual intervention every time
