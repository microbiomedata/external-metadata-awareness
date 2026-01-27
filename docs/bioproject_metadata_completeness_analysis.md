# What Biosamples and Bioprojects Are We Excluding, and Why?

## The Numbers

### Context: We're Already Working with a Filtered Subset

NCBI BioSample contains **~48 million total biosamples**. Our analysis focuses on **~3 million biosamples** that meet initial filters:
- Have environmental triad metadata fields (env_broad_scale, env_local_scale, env_medium) present
- **collection_date >= 2017-01-01** (samples from the last ~8 years)

This is already a **6% subset** of the full NCBI BioSample collection.

**The remaining 45 million biosamples** either:
- Are missing one or more environmental triad fields (most common)
- Were collected before 2017
- Are from domains outside microbiology/environmental science
- Use completely different metadata schemas

Note: Biosamples with all three triad fields populated (even with nonsense values like "xxx" or "banana:sandwich") pass this initial filter and enter our 3M subset. They're only excluded later if the values don't meet quality criteria.

### Within Our 3 Million Subset

The 3M biosamples include any sample with **one or more values** in the environmental triad fields (including samples with multiple values per field, or missing values in some fields).

Out of these ~3 million recent biosamples:

- **506,835 samples (17% of 3M, ~1% of all NCBI)** meet all quality criteria:
  - **Exactly one value** for each environmental triad field (no duplicates, no missing)
  - Have collection_date (>= 2017-01-01)
  - Have lat_lon
  - env_broad_scale uses ENVO prefix
  - env_local_scale uses ENVO or PO prefix
  - env_medium uses ENVO or PO prefix

- **~2.5 million samples (83% of 3M)** are excluded from our analysis

**Why "exactly one"?** We need clean, unambiguous environmental context to align geospatial embeddings (from lat/lon via Google Earth Engine) with semantic embeddings from ENVO and PO terms (via Ontology Lookup Service). Samples with multiple or missing values cannot be cleanly embedded in this joint semantic-geospatial space.

### The Layered Selection

This represents **multiple layers of filtering**:

1. **Temporal filter**: collection_date >= 2017-01-01 → **Focus on recent submissions with modern metadata practices**
2. **Schema filter**: Must have environmental triad fields → **~3M of 48M, already focused on environmental/microbial samples**
3. **Quality filter**: Meet all completeness and ontology criteria → **~500K of 3M have high-quality environmental metadata**

This means we're **excluding the vast majority** even within the recent, environmentally-relevant subset, which raises an important question: **Are these excluded samples fundamentally different from what we're keeping?**

## Why Are Samples Excluded?

### The Biggest Loss: Missing Ontology Terms (NULL values)

**867,857 samples (29% of all samples)** have no CURIEs extracted for any environmental triad field—completely NULL. An additional **~312,000 samples** have CURIEs for some fields but NULL for others:

- 126,141 samples: Missing env_local_scale CURIE (pattern: ENVO-NULL-ENVO)
- 109,431 samples: Only env_broad_scale has CURIE (pattern: ENVO-NULL-NULL)
- 77,744 samples: Missing env_medium CURIE (pattern: ENVO-ENVO-NULL)

**Total with at least one NULL: ~1.4 million samples (47% of dataset)**

These NULLs arise from two very different sources:

1. **Metadata gaps in environmental studies**: Field researchers who didn't provide ontology terms or used free text that couldn't be parsed
2. **Laboratory studies where environmental context is irrelevant**: Genomics/transcriptomics projects where no environmental terms were provided because none were applicable

### Host-Associated Samples: UBERON Anatomy Terms

**Significant exclusion of host-associated microbiome samples:**

- 63,679 samples use pattern ENVO-ENVO-UBERON (human/animal body sites)
- Many other UBERON combinations represent samples from organs, tissues, blood
- These are scientifically valid environmental contexts (e.g., "human gut", "mouse lung") but use anatomy ontology instead of/in addition to ENVO

**This particularly impacts:**
- Human microbiome studies
- Animal microbiome studies
- Disease-associated microbiome research

### Taxonomic Terms: NCBITaxon

Samples using taxonomic identifiers in environmental triads:

- 30,732 samples: NCBITAXON-UBERON-UBERON (organism + anatomy)
- 18,345 samples: NCBITAXON-NCBITAXON-NCBITAXON (all taxonomic)
- Often represents host-associated or symbiotic systems

### Laboratory and Single-Organism Studies

**The fundamental divide:** The excluded samples are dominated by laboratory genomics and transcriptomics projects.

## What Makes Excluded Bioprojects Different?

### Research Type Patterns

**Excluded bioprojects (low metadata completeness):**

**Sample scope:**
- 78.5% eMonoisolate (single-organism studies)
- 15.7% eMultispecies
- Only 3.3% eEnvironment

**Data type:**
- 33.5% transcriptome
- 32.8% genome sequencing
- 16.4% raw sequence reads

**Study focus:**
- Gene expression profiling of specific cultivars/strains
- Population genomics of lab-evolved organisms
- Resequencing and exome capture projects
- Genetic manipulation studies (knockouts, mutations)

**Typical titles:**
- "Sorghum bicolor Keller Gene Expression Profiling - Keller 8.2 transcriptome"
- "Aspergillus niger DeltaxdhA/DeltalxrA Gene Expression Profiling"
- "Zea mays Exome Capture - W10004_0259"

**Organism names:**
- 79.8% specify exact cultivars/strains
- "Populus trichocarpa cultivar:1_90_5_25216"
- "Aspergillus niger strain:DeltasdhA"

**Project scale:**
- Median: 1 biosample per project
- Often a single genotype under controlled conditions

### What's Different About Included Bioprojects?

**Included bioprojects (high metadata completeness):**

**Sample scope:**
- 49.7% eMultispecies
- 33.0% eEnvironment
- 17.3% eMonoisolate

**Data type:**
- 54.8% raw sequence reads
- 16.8% metagenome
- 14.2% genome sequencing

**Study focus:**
- Environmental microbiome surveys
- Spatial/temporal ecological studies
- Community composition analysis
- Habitat characterization

**Typical titles:**
- "Seawater microbial communities from Southern California Bight"
- "Effects of land use and depth on soil organic carbon and microbial communities"
- "microbiome of estuary area in East Java"

**Organism names:**
- 49.3% NULL (community-level, not organism-specific)
- 31.3% generic environmental terms ("soil metagenome", "seawater metagenome")

**Project scale:**
- Median: 10.5 biosamples per project
- Surveying spatial or temporal variation

## Are Excluded Samples "Wildly Different"?

**Yes, but the difference is fundamental to research design, not data quality.**

The excluded 83% are not lower-quality versions of the same science. They represent **fundamentally different research paradigms:**

### Excluded samples predominantly ask:
- "How does this gene function?"
- "What genetic variants exist in this population?"
- "How does this organism respond to X treatment?"

**Where/when doesn't matter** because organisms are grown under controlled, reproducible conditions. Environmental triads would be artificial: env_broad_scale = "laboratory", env_local_scale = "growth chamber", env_medium = "autoclated potting soil" conveys no scientific value.

### Included samples predominantly ask:
- "What organisms live here?"
- "How do communities vary across space/time?"
- "What's the relationship between environment and biodiversity?"

**Where/when is the core variable** being studied. The research question requires spatial-temporal metadata.

## Implications for Bias

### What We're Optimizing For:

**Captured well (17% included):**
- Environmental metagenomics
- Field ecology microbiome studies
- Spatial surveys and monitoring
- Marine/soil/sediment microbiology
- Well-curated environmental context metadata

**Systematically excluded (83%):**

1. **Laboratory molecular biology** - not bias, just different science
   - Genomics, transcriptomics, functional studies
   - Model organisms under controlled conditions
   - No environmental context needed or meaningful

2. **Host-associated microbiomes** - potential bias
   - Human Microbiome Project samples (unless using ENVO exclusively)
   - Animal microbiome studies using anatomy terms
   - Disease microbiome research
   - Could include these by accepting UBERON terms

3. **Plant-associated microbiomes** - partially included
   - Already accepting PO (Plant Ontology) terms
   - Some phyllosphere/rhizosphere studies included
   - May still miss some due to NULL values

4. **Studies with partial metadata** - data quality bias
   - Environmental studies that didn't provide ontology terms
   - Used free text instead of controlled vocabulary
   - Missing lat/lon or collection_date
   - Represents metadata curation gaps, not scientific differences

## The Critical Question: Does This Matter?

**For understanding environmental microbiomes:** The 17% included is highly relevant and appropriate.

**For comprehensive biosample metadata standardization:** We're missing the majority of samples, but most are legitimately outside the scope of environmental metadata requirements.

**For NMDC's mission:** Depends on whether NMDC focuses on:
- Environmental/ecological metagenomics → 17% is the right target
- All sequence-based biology → Missing 83% is a problem
- Host-associated microbiomes → Need to expand ontology acceptance

## Recommendation

The 16-17% inclusion rate is **appropriate given the filtering criteria**, but we should:

1. **Document the exclusion clearly** - Both groups represent valid science
2. **Consider expanding for host-associated samples** - Accept UBERON for body sites
3. **Report large excluded bioprojects** - Understand what major studies we're missing
4. **Distinguish NULL types** - Metadata gaps vs. inapplicable metadata
5. **Assess plant microbiome coverage** - Verify PO acceptance is sufficient

The samples we're keeping are not randomly selected—they're **specifically the ones where environmental metadata is scientifically meaningful**. The excluded samples aren't broken; they're asking different questions.
