# Biosample Flattening Timeline and Technology Evolution (2020-2025)

## Overview

This document traces the evolution of NCBI biosample flattening efforts across multiple repositories, collaborators, and technology stacks from 2020 to 2025. The work has involved consistent collaboration between Mark Andrew Miller (turbomam), Chris Mungall, and Bill Duncan, evolving from research prototypes to production-scale data processing systems.

## Timeline of Major Phases

### Phase 1: INCATools Analysis Framework (2020-2021)
**Repository**: [INCATools/ontology-access-kit](https://github.com/INCATools/ontology-access-kit)
**Key Contributors**: Chris Mungall, turbomam
**Technology Stack**: Python, OAK (Ontology Access Kit), OLS API integration
**Scale**: Research-focused prototype

**Achievements**:
- Established foundational semantic annotation capabilities
- Built OAK-based text annotation for ontology term extraction
- Created reusable ontology access patterns that would influence all subsequent work
- Developed core concepts for automated biosample annotation

### Phase 2: Sample Annotator Development (2021-2022)
**Repository**: [microbiomedata/sample-annotator](https://github.com/microbiomedata/sample-annotator)
**Key Contributors**: turbomam, Bill Duncan, Chris Mungall
**Technology Stack**: Python, MongoDB, OAK, rule-based annotation
**Scale**: NMDC-focused production prototype

**Achievements**:
- First production-oriented biosample processing system
- Integrated OAK with MongoDB for scalable annotation
- Developed environmental context extraction specifically for NMDC workflows
- Established patterns for semantic annotation in production environments

### Phase 3: NMDC Runtime Integration (2022-2023)
**Repository**: [microbiomedata/nmdc-runtime](https://github.com/microbiomedata/nmdc-runtime)
**Key Contributors**: Bill Duncan, turbomam, Chris Mungall
**Technology Stack**: Python, MongoDB, FastAPI, production pipelines
**Scale**: Production system handling thousands of samples

**Achievements**:
- Integrated biosample annotation into NMDC's production data portal
- Scaled annotation to handle real-world NMDC submission workflows
- Developed robust error handling and validation for production use
- Created API endpoints for programmatic access to annotated biosamples

### Phase 4: External Metadata Awareness (2023-2024)
**Repository**: [microbiomedata/external-metadata-awareness](https://github.com/microbiomedata/external-metadata-awareness)
**Key Contributors**: turbomam, with contributions from Chris Mungall and Bill Duncan
**Technology Stack**: Python, MongoDB, DuckDB, XML processing at scale
**Scale**: Massive scale processing (40+ million NCBI biosamples)

**Achievements**:
- Processed complete NCBI biosample corpus (40+ million records)
- Developed sophisticated XML path flattening with selective inclusion/exclusion
- Created environmental triad extraction and normalization pipelines
- Built measurement value extraction using Quantulum3
- Established MongoDB → DuckDB workflows for analytical processing
- Generated comprehensive environmental context voting sheets for standardization

### Phase 5: Berkeley Biosample Analysis (2024)
**Repository**: [turbomam/berkeley-biosample-analysis](https://github.com/turbomam/berkeley-biosample-analysis)
**Key Contributors**: turbomam
**Technology Stack**: Python, pandas, statistical analysis
**Scale**: Research analysis of processed datasets

**Achievements**:
- Advanced statistical analysis of biosample metadata patterns
- Research-focused exploration of metadata quality and completeness
- Development of analytical frameworks for large-scale biosample evaluation

### Phase 6: Universal Database Migration (2025)
**Repository**: [contextualizer-ai/to-duckdb](https://github.com/contextualizer-ai/to-duckdb)
**Key Contributors**: turbomam
**Technology Stack**: Python, DuckDB, universal database connectivity
**Scale**: Generic tooling for any-database → DuckDB migration

**Achievements**:
- Created universal migration framework applicable beyond biosamples
- Established patterns for efficient large-scale database migrations
- Built reusable tooling for analytical database preparation

## Technology Evolution Patterns

### Database Engine Evolution
- **2020-2021**: File-based processing with OAK adapters
- **2021-2022**: MongoDB integration for production scalability
- **2022-2023**: MongoDB with FastAPI for web-scale access
- **2023-2024**: MongoDB + DuckDB hybrid for OLTP/OLAP workflows
- **2024-2025**: Universal migration tooling for analytical database preparation

### XML Processing Paradigms
- **Early Phase**: Element-by-element parsing with manual path handling
- **Intermediate Phase**: Selective flattening with hardcoded exclusions
- **Current Phase**: Comprehensive path analysis with documented inclusion/exclusion rules
- **Scale Evolution**: From hundreds of samples to 40+ million biosamples

### Semantic Annotation Approaches
- **OAK-based**: Consistent use of Ontology Access Kit across all phases
- **Rule-based Enhancement**: Addition of measurement extraction and environmental context parsing
- **Production Integration**: API-based annotation services with validation
- **Analytical Focus**: Bulk processing for research and standardization efforts

## Collaboration Patterns

### Core Contributors
- **turbomam (Mark Andrew Miller)**: Lead developer across all phases, primary architect of large-scale processing
- **Chris Mungall**: Foundational OAK development, semantic annotation expertise, architectural guidance
- **Bill Duncan**: Production system integration, NMDC runtime development, operational scaling

### Cross-Repository Knowledge Transfer
- OAK patterns established in INCATools propagated through all subsequent projects
- MongoDB + annotation patterns from sample-annotator influenced nmdc-runtime design
- Large-scale processing lessons from external-metadata-awareness informed universal migration tooling
- Consistent semantic annotation approaches maintained across all phases

## Technical Achievements and Scale Evolution

### Processing Scale Growth
- **2020-2021**: Dozens to hundreds of samples (research prototype)
- **2021-2022**: Thousands of samples (NMDC production)
- **2022-2023**: Tens of thousands of samples (web-scale production)
- **2023-2024**: 40+ million samples (complete NCBI corpus)
- **2024-2025**: Universal tooling for arbitrary scale migration

### Data Structure Sophistication
- **Early**: Simple key-value attribute extraction
- **Intermediate**: Environmental triad extraction with ontology mapping
- **Advanced**: Measurement value extraction with unit normalization
- **Current**: Comprehensive flattening with documented path inclusion/exclusion rules

### Infrastructure Evolution
- **Research Phase**: Local processing with file-based storage
- **Production Phase**: Distributed MongoDB with API access
- **Analytics Phase**: Hybrid MongoDB/DuckDB for OLTP/OLAP workflows
- **Universal Phase**: Database-agnostic migration frameworks

## NCBI Biosample XML Path Processing

### Path Inclusion and Exclusion Documentation

The comprehensive approach to NCBI biosample XML path handling has evolved significantly over the timeline. The most definitive documentation for XML path inclusion and exclusion rules is maintained on NERSC:

**Primary Documentation**: https://portal.nersc.gov/cfs/m3408/biosamples_duckdb/README.md

This NERSC resource provides the definitive specification for which XML paths are included in flattened biosample collections and which are excluded, representing the culmination of years of iterative development and refinement.

**Additional NERSC Resource**: https://portal.nersc.gov/project/m3513/biosample

### Path Processing Evolution

The handling of XML paths has become increasingly sophisticated:

1. **Early Phases (2020-2022)**: Manual identification of relevant paths
2. **Production Phases (2022-2023)**: Hardcoded inclusion/exclusion lists
3. **Current Phase (2023-2025)**: Documented, systematic path analysis with comprehensive coverage

### Excluded Path Categories

Based on code analysis and NERSC documentation, excluded paths typically include:
- Administrative metadata (submission dates, update timestamps)
- Internal NCBI identifiers and cross-references
- Redundant hierarchical containers
- System-specific formatting elements
- Empty or placeholder attributes

### Included Path Focus

Included paths prioritize:
- Scientific metadata (environmental context, sample characteristics)
- Measurement values with units
- Taxonomic information
- Geographic and temporal data
- Experimental conditions and protocols

## Current Collection Architecture and Strategic Filtering (2024-2025)

### Subset Design for Google Earth Environment Embeddings Alignment

The current external-metadata-awareness collections represent a **strategically filtered subset** of the complete NCBI biosample corpus (~45 million records), optimized for alignment with Google Earth environment embeddings data. The working dataset contains approximately **3 million biosamples** that meet specific criteria:

**Primary Filtering Criteria:**
- **Recent temporal range**: Biosamples with recent submission/update dates
- **Complete environmental context triads**: Records containing all three environmental context components (env_broad_scale, env_local_scale, env_medium)
- **Geographic completeness**: Samples with sufficient location data for Google Earth coordinate matching
- **Quality thresholds**: Minimum metadata completeness requirements

### Collection Categories and Design Rationale

#### 1. Core Analytical Collections (Highest Priority)

**`measurement_results_skip_filtered` - CRITICAL COLLECTION**
- **Purpose**: Processes measurement-like attributes into structured values and units
- **Source**: Derived from `biosamples_attributes`
- **Processing**: Excludes attributes where harmonized_name is already designated as non-measurement content
- **Known Limitations**: Quantulum3 unit extraction sometimes differs significantly from submitter-provided values
- **Importance**: One of the two most important collections for analytical use

**`env_triads_flattened` - CRITICAL COLLECTION**
- **Purpose**: Normalizes environmental context values (env_broad_scale, env_local_scale, env_medium) to linked data vocabularies
- **Source**: Derived from `biosamples_attributes`
- **Processing**: Maps submitted values to OBO Foundry ontology classes and other controlled vocabularies
- **Scale**: 9.3M normalized component records from 3M biosamples
- **Importance**: One of the two most important collections; essential for environmental standardization efforts

#### 2. Relationship and Reference Collections
**Purpose**: Normalized list-like data that would be difficult to flatten into main biosample table

**`biosamples_attributes`** - Source collection for both critical analytical collections above
- **Purpose**: All attribute-value pairs extracted from biosamples
- **Scale**: 52M+ records representing complete attribute extraction
- **Relationship**: Supplement to `biosamples_flattened` for list-like biosample relationships

**`biosamples_ids`**
- **Purpose**: Extracted ID/accession mappings from biosample records
- **Relationship**: Supplement to `biosamples_flattened` for list-like ID relationships

**`biosamples_links`**
- **Purpose**: Link/URL extractions from biosample records
- **Relationship**: Supplement to `biosamples_flattened` for list-like link relationships

**`sra_biosamples_bioprojects`**
- **Purpose**: Relational mapping derived from NCBI BioProject metadata (Amazon S3)
- **Scale**: 29M+ records linking SRA, BioSample, and BioProject entities
- **Strategic Value**: Enables counting bioprojects per attribute to avoid overweighting attributes used by many samples from single studies

#### 3. Content Analysis Collections

**`content_pairs_aggregated`**
- **Purpose**: Shows all unique content values that appear in attributes by harmonized_name
- **Context**: All attributes have user-submitted attribute_name, but NCBI only harmonizes subset to MIxS-based fields
- **Harmonization Method**: NCBI alignment enabled by synonyms in flattened NCBI attribute definitions collection
- **Scale Limitation**: Computationally prohibitive for complete 45M corpus

**`attribute_harmonized_pairings`**
- **Purpose**: Mapping relationships between attribute name variants and their harmonized forms

#### 4. Schema Documentation Collections
**Purpose**: Metadata about metadata structure, not content
- `ncbi_attributes_flattened`: NCBI attribute definitions and specifications
- `ncbi_packages_flattened`: NCBI package schema specifications
- `global_mixs_slots`: MIxS schema slot definitions
- `global_nmdc_slots`: NMDC schema slot definitions

#### 2. Usage Analytics Collections
**Purpose**: Statistical analysis of attribute utilization across biosamples/bioprojects
- `harmonized_name_usage_stats`: Frequency analysis of harmonized attribute names
- `harmonized_name_dimensional_stats`: Dimensional analysis of attribute usage patterns

#### 3. Measurement Processing Collections
**Purpose**: Extracted and normalized measurement values with quality filtering

**Filtered for Practicality:**
- `measurement_results_skip_filtered`: **Excludes** attempts to parse attributes where harmonized_name is already designated as non-measurement content
- `measurement_evidence_percentages`: Aggregated confidence scores for measurement detection

**Known Limitations:**
- **Quantulum3 unit extraction**: Units extracted are sometimes significantly different from submitter-provided values
- **Scale constraints**: Some collections impractical to generate for complete 45M corpus due to computational complexity

#### 4. Environmental Context Collections
**Purpose**: Normalized environmental triads for standardization efforts

**Hierarchical Relationships:**
- `biosamples_flattened` → `biosamples_attributes` → `env_triads_flattened`
- Each level represents progressive normalization and filtering
- `env_triads_flattened`: Fully normalized subset optimized for DuckDB export and Google Earth alignment

#### 5. Content Relationship Collections
**Purpose**: Aggregated content analysis and relationship mapping
- `content_pairs_aggregated`: **Example of scale limitation** - computationally prohibitive for 45M corpus
- `attribute_harmonized_pairings`: Relationship mappings between attribute variants

#### 6. Highly Duplicative Collections
**Purpose**: Multiple representations for different analytical use cases

**Measurement Evidence Chain:**
- `mixed_content_counts` → `unit_assertion_counts` → `measurement_evidence_percentages`
- Progressive aggregation with value-added analysis at each stage
- High duplication but serves different analytical granularities

### Future Evolution Considerations

#### Scalability Constraints
1. **Complete Corpus Processing**: Some analytical collections cannot be generated for full 45M biosamples
2. **Computational Limits**: Content aggregation operations hit memory/time boundaries at scale
3. **Storage Optimization**: Hierarchical collections balance completeness vs. practical access patterns

#### Quality Improvement Roadmap
1. **Unit Extraction Enhancement**: Replace/supplement Quantulum3 with improved measurement parsing
2. **Temporal Filtering Refinement**: Dynamic date ranges based on Google Earth data availability
3. **Geographic Coverage Expansion**: Broaden environmental context criteria while maintaining alignment quality

#### Integration Targets
- **Google Earth Environment Embeddings**: Primary alignment target for current subset
- **DuckDB Export Optimization**: Collections designed for efficient analytical database migration
- **Community Standardization**: Environmental context voting sheets for broader adoption

### Strategic Documentation Value

This filtering approach represents a **pragmatic compromise** between:
- **Computational Feasibility**: Processing constraints at 45M record scale
- **Research Alignment**: Specific integration with Google Earth embeddings
- **Quality Thresholds**: Complete environmental triads for meaningful analysis
- **Temporal Relevance**: Recent data more likely to align with current environmental monitoring

The subset serves as a **high-quality reference implementation** that can inform scaling decisions and quality standards for future complete corpus processing.

## DuckDB Export Ecosystem

### NCBI Biosample DuckDB (Primary Output)

The canonical output from this processing pipeline is **DuckDB databases** containing flattened NCBI biosample data:
- **Generation**: Via `mongodb_biosamples_to_duckdb.py` (this repo) and `to-duckdb` universal migration framework
- **NERSC Hosting**: https://portal.nersc.gov/cfs/m3408/biosamples_duckdb/ (NERSC projects m3408, m3513)
- **Content**: Flattened biosamples with environmental triads, measurements, and normalized attributes
- **Scale**: 3M strategically filtered biosamples from 45M total corpus

### GOLD Database DuckDBs (Two Approaches)

**API-based DuckDB:**
- **Entity Coverage**: Studies, Projects, and Biosamples (excludes organism/isolate records)
- **Field Richness**: 50+ biosample fields including complete MIxS environmental context triads
- **Processing**: GOLD API → MongoDB → DuckDB via gold-tools and to-duckdb
- **Use Case**: Rich metadata analysis for biosample-linked entities

**Excel-based DuckDB:**
- **Entity Coverage**: All entity types including organism/isolate records
- **Field Coverage**: ~15 fields per entity (minimal but portable)
- **Inspiration**: Valerie Parker's (ct-parker) BERtron PostgreSQL ingestion methods
- **Processing**: GOLD Excel download → flattening → DuckDB
- **Use Case**: Comprehensive entity coverage with lightweight portability

### NMDC Database DuckDB

**NMDC Flattened DuckDB:**
- **Source**: NMDC production MongoDB (authenticated access)
- **Processing**: Via sample-annotator, nmdc-runtime integration, and to-duckdb migration
- **Content**: NMDC biosample_set and related workflow/annotation collections
- **Integration**: Aligned with NMDC submission schema and LinkML models

### Cross-Database Integration

All three database sources (NCBI, GOLD, NMDC) follow similar flattening principles:
- Selective XML/JSON path extraction
- Environmental context normalization to ontology terms
- Measurement value and unit parsing
- DuckDB format for analytical portability and performance

### Important: Schema Stability Notice

**Naming conventions are not yet stable.** Database names, collection names, table names, field names, and column names are subject to change as the ecosystem evolves. Users should:
- Expect schema variations between versions
- Document the specific version/date of data exports used in analyses
- Verify field names and structures when updating to newer exports
- Contact maintainers before building production dependencies on specific naming conventions

This documentation captures the current state but does not guarantee stability of naming or structure in future releases.

## Current State and Future Directions

As of 2025, the biosample flattening ecosystem represents a mature, multi-faceted approach to large-scale biological metadata processing:

- **Production Systems**: Operational in NMDC with thousands of annotated samples
- **Research Infrastructure**: Strategic subset processing (3M from 45M corpus) optimized for specific research alignments
- **Standardization Efforts**: Environmental context voting sheets for community standardization
- **Universal Tooling**: Database-agnostic migration frameworks for broader applicability

The work demonstrates successful evolution from research prototypes to production systems, maintaining consistent semantic annotation approaches while scaling to handle strategically filtered subsets of the complete corpus of public biological metadata.

---

*This timeline represents collaborative work spanning 5 years and multiple institutions, demonstrating the evolution of biological metadata processing from research prototypes to production-scale systems handling millions of samples.*