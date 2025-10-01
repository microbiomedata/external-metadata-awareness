# biosamples_flattened Path Inclusion Analysis
*Analysis Date: 2025-09-30*

## Overview
Analysis of which XML paths from `ncbi-biosample-xml-paths.tsv` are processed into the `biosamples_flattened` collection by `mongo-js/flatten_biosamples.js`.

## Processing Script: `flatten_biosamples.js`

The script creates `biosamples_flattened` by projecting specific paths and conditionally processing attributes with harmonized_name.

---

## ✅ INCLUDED PATHS (Processed into biosamples_flattened)

### Root-Level Attributes (Direct 1:1 mapping)
All of these are unconditionally included:

| XPath | Collection Field | Count | Notes |
|-------|------------------|-------|-------|
| `/BioSampleSet/BioSample@access` | `access` | 48,182,902 | Access level |
| `/BioSampleSet/BioSample@accession` | `accession` | 48,182,902 | Primary identifier |
| `/BioSampleSet/BioSample@id` | `id` | 48,182,902 | Numeric ID |
| `/BioSampleSet/BioSample@last_update` | `last_update` | 48,182,902 | Timestamp |
| `/BioSampleSet/BioSample@publication_date` | `publication_date` | 48,182,902 | Publication date |
| `/BioSampleSet/BioSample@submission_date` | `submission_date` | 48,156,102 | Submission date |

### Package Information
| XPath | Collection Field | Count |
|-------|------------------|-------|
| `/BioSampleSet/BioSample/Package#text` | `package_content` | 48,182,902 |

### Status Information
| XPath | Collection Field | Count |
|-------|------------------|-------|
| `/BioSampleSet/BioSample/Status@status` | `status_status` | 48,182,902 |
| `/BioSampleSet/BioSample/Status@when` | `status_when` | 48,182,902 |

### Reference Status
| XPath | Collection Field | Count |
|-------|------------------|-------|
| `/BioSampleSet/BioSample@is_reference` | `is_reference` | 2,331 |

### Curation Information (When Present)
| XPath | Collection Field | Count |
|-------|------------------|-------|
| `/BioSampleSet/BioSample/Curation@curation_date` | `curation_date` | 13,994 |
| `/BioSampleSet/BioSample/Curation@curation_status` | `curation_status` | 13,994 |

### Owner Information (Partial)
| XPath | Collection Field | Count | Notes |
|-------|------------------|-------|-------|
| `/BioSampleSet/BioSample/Owner/Name@abbreviation` | `owner_abbreviation` | 15,298,937 | **INCLUDED** |
| `/BioSampleSet/BioSample/Owner/Name#text` | `owner_name` | 38,679,299 | **INCLUDED** |
| `/BioSampleSet/BioSample/Owner/Name@url` | `owner_url` | 3,377,357 | **INCLUDED** |

### Description Fields (Partial)
| XPath | Collection Field | Count | Notes |
|-------|------------------|-------|-------|
| `/BioSampleSet/BioSample/Description/Title#text` | `description_title` | 48,182,902 | **INCLUDED** |
| `/BioSampleSet/BioSample/Description/Organism/OrganismName#text` | `organism_name` | 37,573,824 | **INCLUDED** |
| `/BioSampleSet/BioSample/Description/Organism@taxonomy_id` | `taxonomy_id` | 48,182,902 | **INCLUDED** |
| `/BioSampleSet/BioSample/Description/Organism@taxonomy_name` | `taxonomy_name` | 48,182,902 | **INCLUDED** |
| `/BioSampleSet/BioSample/Description/Comment/Paragraph#text` | `description_comment` | 13,608,120 | **INCLUDED** (concatenated) |

### Attributes (Conditional - ONLY with harmonized_name)
| XPath | Collection Field | Count | Processing |
|-------|------------------|-------|------------|
| `/BioSampleSet/BioSample/Attributes/Attribute@harmonized_name` | Dynamic field names | 439,379,948 | **INCLUDED** as top-level fields |
| `/BioSampleSet/BioSample/Attributes/Attribute#text` | Values for above | 689,438,723 | **INCLUDED** when harmonized_name exists |

**Filter Logic (Lines 75-82):**
```javascript
cond: {
    $and: [
        {$ne: ["$$attr.harmonized_name", null]},
        {$ne: ["$$attr.content", null]},
        {$eq: [{$type: "$$attr.harmonized_name"}, "string"]},
        {$eq: [{$type: "$$attr.content"}, "string"]}
    ]
}
```

**Result**: Only **439,379,948** of **689,999,589** total attributes are processed (63.6% coverage).
**Excluded**: **250,619,641 attributes** without `harmonized_name` are not saved to biosamples_flattened.

---

## ❌ EXCLUDED PATHS (NOT in biosamples_flattened)

### 1. Owner/Contacts Subtree (Almost Complete Exclusion)
**You are correct** - These are NOT processed into biosamples_flattened:

| XPath | Count | Status |
|-------|-------|--------|
| `/BioSampleSet/BioSample/Owner/Contacts` | 20,485,937 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Owner/Contacts/Contact` | 20,486,862 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Owner/Contacts/Contact/Name` | 19,746,330 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Owner/Contacts/Contact/Name/First` | 19,677,265 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Owner/Contacts/Contact/Name/Last` | 19,746,330 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Owner/Contacts/Contact/Name/Middle` | 3,039,956 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Owner/Contacts/Contact@lab` | 807,266 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Owner/Contacts/Contact/Address` | 66,921 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Owner/Contacts/Contact/Address/Street` | 66,921 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Owner/Contacts/Contact@phone` | 41,354 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Owner/Contacts/Contact@fax` | 26,391 | ❌ **EXCLUDED** |

**Impact**: **~20M contact records** completely excluded from biosamples_flattened.

### 2. Description/Comment/Table Subtree (Complete Exclusion)
**You are correct** - Table structures are NOT processed:

| XPath | Count | Status |
|-------|-------|--------|
| `/BioSampleSet/BioSample/Description/Comment/Table` | 44,078 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Description/Comment/Table/Body` | 44,078 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Description/Comment/Table/Header` | 44,078 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Description/Comment/Table/Caption` | 44,078 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Description/Comment/Table/Body/Row` | 593,517 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Description/Comment/Table/Body/Row/Cell` | 5,214,734 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Description/Comment/Table/Header/Cell` | 390,914 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Description/Comment/Table@class` | 39,853 | ❌ **EXCLUDED** |

**Impact**: **~5.2M table cells** completely excluded from biosamples_flattened.

### 3. Description/Synonym (Complete Exclusion)
| XPath | Count | Status |
|-------|-------|--------|
| `/BioSampleSet/BioSample/Description/Synonym` | 385,583 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Description/Synonym#text` | 385,583 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Description/Synonym@db` | 385,583 | ❌ **EXCLUDED** |

**Impact**: **~386K synonym records** excluded from biosamples_flattened.

### 4. Models Information (Complete Exclusion)
| XPath | Count | Status |
|-------|-------|--------|
| `/BioSampleSet/BioSample/Models/Model` | 50,726,635 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Models/Model#text` | 50,726,635 | ❌ **EXCLUDED** |
| `/BioSampleSet/BioSample/Models/Model@version` | 103,740 | ❌ **EXCLUDED** |

**Impact**: **~50.7M model references** excluded from biosamples_flattened.

### 5. Ids Subtree (Complete Exclusion from biosamples_flattened)
| XPath | Count | Status | Alternative Processing |
|-------|-------|--------|------------------------|
| `/BioSampleSet/BioSample/Ids/Id` | 119,651,078 | ❌ **EXCLUDED** | ✅ **Processed by `flatten_biosamples_ids.js`** |
| `/BioSampleSet/BioSample/Ids/Id#text` | 119,651,078 | ❌ **EXCLUDED** | ✅ **Processed separately** |
| `/BioSampleSet/BioSample/Ids/Id@db` | 103,917,360 | ❌ **EXCLUDED** | ✅ **Processed separately** |
| `/BioSampleSet/BioSample/Ids/Id@db_label` | 25,856,379 | ❌ **EXCLUDED** | ✅ **Processed separately** |
| `/BioSampleSet/BioSample/Ids/Id@is_primary` | 48,182,902 | ❌ **EXCLUDED** | ✅ **Processed separately** |
| `/BioSampleSet/BioSample/Ids/Id@is_hidden` | 9,515,938 | ❌ **EXCLUDED** | ✅ **Processed separately** |

**Note**: As you mentioned, IDs are processed unconditionally by `flatten_biosamples_ids.js` into `biosamples_ids` collection.

### 6. Links Subtree (Complete Exclusion from biosamples_flattened)
| XPath | Count | Status | Alternative Processing |
|-------|-------|--------|------------------------|
| `/BioSampleSet/BioSample/Links/Link` | 28,832,627 | ❌ **EXCLUDED** | ✅ **Processed by `flatten_biosamples_links.js`** |
| `/BioSampleSet/BioSample/Links/Link#text` | 28,821,145 | ❌ **EXCLUDED** | ✅ **Processed separately** |
| `/BioSampleSet/BioSample/Links/Link@type` | 28,832,627 | ❌ **EXCLUDED** | ✅ **Processed separately** |
| `/BioSampleSet/BioSample/Links/Link@label` | 28,767,967 | ❌ **EXCLUDED** | ✅ **Processed separately** |
| `/BioSampleSet/BioSample/Links/Link@target` | 23,368,609 | ❌ **EXCLUDED** | ✅ **Processed separately** |
| `/BioSampleSet/BioSample/Links/Link@submission_id` | 94 | ❌ **EXCLUDED** | ✅ **Processed separately** |

**Note**: As you mentioned, Links are processed unconditionally by `flatten_biosamples_links.js` into `biosamples_links` collection.

### 7. Attributes Without harmonized_name (Conditional Exclusion)
| XPath | Total Count | Included Count | Excluded Count | Status |
|-------|-------------|----------------|----------------|--------|
| `/BioSampleSet/BioSample/Attributes/Attribute` | 689,999,589 | 439,379,948 | **250,619,641** | **36.3% EXCLUDED** |
| `/BioSampleSet/BioSample/Attributes/Attribute@attribute_name` | 689,999,589 | ~439M | ~250M | Some excluded |
| `/BioSampleSet/BioSample/Attributes/Attribute@display_name` | 439,379,948 | 439,379,948 | 0 | Matches harmonized |
| `/BioSampleSet/BioSample/Attributes/Attribute@unit` | 191,867 | Subset | Subset | Only if harmonized_name exists |

**Note**: As you mentioned, ALL attributes are processed unconditionally by `flatten_biosample_attributes.py` into `biosamples_attributes` collection, including those without `harmonized_name`.

---

## Summary Statistics

### Total XML Paths in TSV: 89 unique paths

### Included in biosamples_flattened:
- **Direct mapped paths**: 21 paths
- **Harmonized attributes**: Dynamic fields (439M attribute instances)
- **Coverage**: ~29 distinct path patterns

### Excluded from biosamples_flattened:
- **Owner/Contacts**: ~10 paths, 20M+ records
- **Comment/Table**: ~10 paths, 5.2M+ cells
- **Synonyms**: 3 paths, 386K records
- **Models**: 3 paths, 50.7M records
- **Ids**: 6 paths (processed separately)
- **Links**: 6 paths (processed separately)
- **Non-harmonized Attributes**: 250M+ attribute instances
- **Total excluded paths**: ~38 distinct path patterns

### Processing Distribution:
- **biosamples_flattened**: 29 path patterns (~33%)
- **biosamples_ids**: 6 path patterns (unconditional processing)
- **biosamples_links**: 6 path patterns (unconditional processing)
- **biosamples_attributes**: All attributes (unconditional processing)
- **Completely excluded**: ~20 path patterns (22%)

---

## Key Findings

### Your Observations Are Correct:

1. ✅ **Contact information is NOT captured** in biosamples_flattened
   - 20M+ contact records excluded
   - First/Last/Middle names not saved
   - Phone, fax, address, lab information lost

2. ✅ **Table structures are NOT captured** in biosamples_flattened
   - 44K tables with 5.2M cells excluded
   - Table headers, captions, body rows all excluded

3. ✅ **Attributes require harmonized_name** for inclusion
   - 250M+ non-harmonized attributes excluded from biosamples_flattened
   - BUT: All attributes (including non-harmonized) processed by separate script

4. ✅ **Ids and Links processed separately**
   - Not in biosamples_flattened
   - Unconditionally processed into dedicated collections

### Design Rationale (Inferred):

**biosamples_flattened optimizes for:**
- Analytical queries on harmonized scientific metadata
- Flat, tabular structure suitable for DuckDB export
- Core biosample identification and taxonomy
- Owner organization (but not contact details)
- Scientific attributes with NCBI harmonization

**Excluded data patterns:**
- **List-like relationships** (Ids, Links) → Separate collections for normalization
- **Personal information** (Contacts) → Privacy/GDPR considerations?
- **Structured data** (Tables) → Complex to flatten, rare (44K of 48M)
- **Synonyms** → Potentially redundant with harmonized names
- **Models** → Metadata about metadata, not scientific content
- **Non-harmonized attributes** → Separate collection for complete preservation

---

## Recommendations for Documentation

This analysis should be added to the biosample-flattening-timeline document's "NCBI Biosample XML Path Processing" section to provide definitive documentation of inclusion/exclusion rules.

The NERSC documentation (https://portal.nersc.gov/cfs/m3408/biosamples_duckdb/README.md) likely contains authoritative rationale for these design decisions.
