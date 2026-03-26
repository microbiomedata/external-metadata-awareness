# Repository Alignment & Priority Roadmap

**Generated**: 2025-10-02
**Purpose**: Align issues, documentation, and code; provide clear next-step priorities

---

## Executive Summary

This repository has **46 open issues** spanning 14 months (Aug 2024 - Oct 2025). After auditing all empty and short-body issues, here's a framework for deciding what to work on next.

### Current State Assessment

**Strengths:**
- ✅ Core functionality working: biosample normalization (#214-221 closed)
- ✅ DuckDB export pipeline functional (PR #32 merged)
- ✅ MongoDB collections populated and indexed
- ✅ Environmental context voting sheets generated
- ✅ Issues now have context (just added to 18 issues today)

**Gaps:**
- ❌ Missing semantic similarity functionality (#11, #13, #21)
- ❌ No EBI/ENA integration (#1)
- ❌ Stale/missing files referenced in issues (#18, #21, #114)
- ❌ Inconsistent MongoDB connection patterns (#176)
- ❌ No automated data refresh strategy (#63, #64)

---

## Issue Categorization Framework

### Category 1: IMMEDIATE - Active Work Threads ⚡
*Issues directly connected to recently merged work or blocking current workflows*

| Issue | Title | Why Immediate | Effort |
|-------|-------|---------------|--------|
| #216 | Integrate date/coordinate normalization into MongoDB biosample flattening pipeline | Extends just-completed normalization work (#214-215) | Medium |
| #218 | Handle date ranges and multi-value collection dates | Known limitation from #214 work | Small |
| #219 | Investigate biosamples with missing collection_date | Data quality issue discovered in #214 | Small |
| #220 | Add lat_lon requirement to future biosample flattening/normalization pipelines | Architectural decision from #214 | Small |
| #221 | Define timezone handling strategy | Documented limitation from #214, needs resolution | Small |

**Suggested Action**: Complete the normalization work cluster. Total effort ~2-3 weeks.

---

### Category 2: INFRASTRUCTURE - Foundation Issues 🏗️
*Technical debt and consistency problems affecting multiple workflows*

| Issue | Title | Why Important | Effort | Blockers |
|-------|-------|---------------|--------|----------|
| #176 | Unified strategy for caching study, biosample, etc. metadata in MongoDB | Affects every MongoDB script | Large | None |
| #203 | Replace print() statements with proper logging | Code quality, debugging | Medium | None |
| #202 | Add code quality standards and automated checks | Prevents regressions | Medium | None |
| #63 | Strategy for keeping supplementary MongoDB collections up to date | Data freshness | Medium | #176 |
| #64 | Strategy for keeping Biosample DuckDB up to date | Data freshness | Medium | #176 |
| #183 | Document the process of loading this repo's MongoDB from scratch | Reproducibility | Small | #176 |

**Suggested Action**: Tackle #176 first (MongoDB connection unification), then #203 (logging), then automated refresh strategies.

---

### Category 3: FEATURE REQUESTS - Enhancement Opportunities 🎯
*New capabilities that extend functionality*

| Issue | Title | Priority | Rationale |
|-------|-------|----------|-----------|
| #159 | Add tqdm to new_bioportal_curie_mapper.py | HIGH | User experience, quick win |
| #62 | Index more fields in supplementary MongoDB | MEDIUM | Query performance |
| #200 | Add CSV export functionality for flattened GOLD collections | MEDIUM | Data accessibility |
| #1 | Load EBI/ENA biosample metadata specifications | LOW | Major scope expansion |
| #68 | Regenerate Simon's SRA wishlist | LOW | One-off analysis task |

**Suggested Action**: Quick wins first (#159), then performance (#62), defer scope expansions (#1).

---

### Category 4: RESEARCH QUESTIONS - Needs Investigation 🔬
*Issues requiring analysis before implementation*

| Issue | Title | Action Needed |
|-------|-------|---------------|
| #156 | Obsolete flag not present in some annotations | Verify if still occurring, create test cases |
| #157 | Ignore some annotations like ENVO 'gut' | Define semantic filtering criteria |
| #158 | OAK annotate text configuration for whole words | Create gold-standard test set, measure sensitivity/specificity |
| #11, #13, #21 | Semantic similarity functionality | Research requirements, evaluate libraries (OAK semsim, embeddings) |
| #12 | Review anthropogenic classes in env_local_scale | Domain expert review needed (@sierra-moxon @cmungall) |

**Suggested Action**: These need requirements gathering before coding. Consider creating RFCs or design docs.

---

### Category 5: DOCUMENTATION DEBT - Knowledge Capture 📚
*Missing or outdated documentation*

| Issue | Title | Complexity |
|-------|-------|------------|
| #191 | Document measurement analysis on NCBI Biosamples | Medium |
| #194 | Document measurement analysis (for UCUM alignment) for all sources | Medium |
| #204 | Document using DuckDB with SRA metadata parquet files | Small |
| #42 | Review dependencies and update documentation | Small |

**Suggested Action**: Low-hanging fruit - #204 and #42 can be done quickly.

---

### Category 6: STALE/QUESTIONABLE - May Close 🗑️
*Issues that may no longer be relevant*

| Issue | Title | Reason |
|-------|-------|--------|
| #18 | jaccard_distance in file doesn't look right | File doesn't exist |
| #40 | See followup actions from PR #32 | PR merged, no specific actions listed |
| #25 | Some scripts still access Biosample PostgreSQL | PostgreSQL deprecated |
| #132 | Some mixs preferred unit annotations are blank | host_common_name/samp_name aren't measurements |

**Suggested Action**: Review with stakeholders, likely close most of these.

---

## Recommended Priority Sequence

### Phase 1: Complete Active Work (1-2 months)
1. ✅ Issues #216-221 (biosample normalization completion)
2. ✅ Issue #159 (add tqdm - quick win)
3. ✅ Issues #204, #42 (documentation quick wins)

### Phase 2: Infrastructure Stabilization (2-3 months)
1. ✅ Issue #176 (unified MongoDB connection strategy)
2. ✅ Issue #203 (logging framework)
3. ✅ Issue #202 (code quality checks)
4. ✅ Issues #63, #64 (automated refresh strategies)
5. ✅ Issue #183 (MongoDB setup documentation)

### Phase 3: Selective Feature Work (2-3 months)
1. ✅ Issue #62 (MongoDB indexing)
2. ✅ Issue #200 (GOLD CSV export)
3. ✅ Issues #191, #194 (measurement documentation)
4. ✅ Research questions requiring design (#11, #13, #21, #157, #158)

### Phase 4: Scope Expansion (if needed)
1. ❓ Issue #1 (EBI/ENA integration) - major undertaking
2. ❓ Other large feature requests

---

## Alignment Actions Completed Today

### Issues Context Added (18 issues)
- #1, #11, #12, #13, #18, #21, #40, #62, #68, #114, #132, #156, #157, #158, #159, #176
- All previously empty issues now have code evidence and current status

### Cross-References Created
- Linked semantic similarity issues: #11, #13, #21
- Linked OAK annotation issues: #156, #157, #158, #159
- Linked biosample normalization issues: #216, #218-221

---

## Quick Decision Matrix

**Question**: Should I work on this issue?

```
┌─────────────────────────────┬──────────────────────────┬────────────────┐
│ Question                    │ Answer                   │ Priority       │
├─────────────────────────────┼──────────────────────────┼────────────────┤
│ Extends recent work?        │ Yes → #216-221           │ IMMEDIATE      │
│ Blocks other work?          │ Yes → #176               │ HIGH           │
│ Quick win?                  │ Yes → #159, #204, #42    │ HIGH           │
│ Code quality?               │ Yes → #203, #202         │ MEDIUM-HIGH    │
│ Data freshness?             │ Yes → #63, #64           │ MEDIUM         │
│ Domain expert needed?       │ Yes → #12, #14, #15      │ DEFER/ASK      │
│ Major scope expansion?      │ Yes → #1                 │ LOW/DEFER      │
│ File doesn't exist?         │ Yes → #18, #21           │ CLOSE?         │
└─────────────────────────────┴──────────────────────────┴────────────────┘
```

---

## Repository Health Metrics

**Issues**: 46 open (now all with context)
**Python Scripts**: 54 files
**Makefiles**: 4 with TODOs
**Documentation**: 60+ markdown files (some redundant)
**Recent Activity**: High (10 issues created in past week)

**Recommendation**: Focus on **completion over addition**. The repository has strong foundations but needs consolidation.

---

## Next Steps

1. **Review this roadmap** - Does the categorization align with your priorities?
2. **Pick a phase** - Which phase (1-4) matches your current goals?
3. **Start small** - Begin with Phase 1 or quick wins (#159, #204, #42)
4. **Close stale issues** - Review Category 6 for candidates
5. **Create tracking issue** - Consider a meta-issue to track Phase 1 progress

---

## Files That Could Be Consolidated/Archived

**Documentation cleanup** tracked in [#318](https://github.com/microbiomedata/external-metadata-awareness/issues/318).
Session notes, outdated DuckDB docs, and duplicate files removed in docs cleanup PR.

**unorganized/** directory - as the name suggests, needs organization

---

## Maintenance Recommendations

### Regular (Monthly):
- Review open issues, close completed/stale ones
- Update CLAUDE.md with new patterns/findings
- Refresh MongoDB/DuckDB data

### Quarterly:
- Dependency updates (#42)
- Documentation audit
- Performance review

### Annually:
- Major refactoring (e.g., #176 MongoDB unification)
- Scope expansions (e.g., #1 EBI/ENA)
