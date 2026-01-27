# NMDC Biosample API Enrichment Strategy

## Executive Summary

This document outlines a comprehensive strategy for integrating API-sourced data into NMDC Biosample records, building on the crawl-first deterministic enrichment philosophy and extending it to support millions of biosample records across multiple data sources. The strategy addresses validation of asserted vs. API-sourced data, recommends new schema slots, identifies enrichment opportunities for under-populated fields, and provides a framework for critical minerals proximity analysis.

## Current State Analysis

### NMDC Schema Coverage
- **Total NMDC Biosample slots**: 577
- **Populated slots in current dataset**: 131 (22.7%)
- **Missing/under-populated slots**: 446 (77.3%)
- **Key gap**: Chemical administration data stored in separate collection

### Existing crawl-first Capabilities
The crawl-first project demonstrates successful API integration patterns:
- **Geospatial enrichment**: Elevation, OSM features, reverse geocoding
- **Environmental context**: Soil types, land cover classification, weather data
- **Publication tracking**: DOI resolution, full-text retrieval
- **Ontology integration**: ENVO term matching
- **Quality validation**: Coordinate/elevation cross-validation
- **Comprehensive caching**: Preventing redundant API calls

## Core Strategy Framework

### 1. Data Provenance and Confidence Architecture

#### Provenance Tracking
```yaml
slot_name_enriched:
  asserted_value: "original value from source"
  api_enrichments:
    - source: "api_name"
      method: "lookup_method"
      confidence: 0.95
      value: "enriched_value"
      timestamp: "2024-08-21T00:00:00Z"
      validation_status: "validated|conflict|unverified"
```

#### Confidence Scoring Framework
- **0.9-1.0**: Direct API match with validation
- **0.7-0.9**: Indirect inference with supporting evidence
- **0.5-0.7**: Probabilistic match requiring review
- **0.0-0.5**: Low confidence, flag for manual review

### 2. Validation Methodology

#### Asserted vs. API-Sourced Data Validation
1. **Coordinate Validation**: Cross-reference lat/lon with elevation APIs and reverse geocoding
2. **Temporal Validation**: Verify collection dates against available environmental data
3. **Semantic Validation**: Check environmental context consistency (env_broad_scale → env_local_scale → env_medium)
4. **Ontological Validation**: Validate ENVO terms and suggest corrections for deprecated terms

#### Conflict Resolution Protocol
- **Priority Order**: Asserted data > High-confidence API > Low-confidence API
- **Flag Conflicts**: When API data contradicts asserted data with >0.8 confidence
- **Human Review Queue**: Conflicts requiring domain expert evaluation

### 3. New Slot Recommendations

#### Critical Minerals Proximity Analysis
Based on USGS 2022 Critical Minerals List, add these geospatial analysis slots:

```yaml
# Critical Minerals Proximity
critical_minerals_nearby:
  has_raw_value: "distance_km_to_nearest"
  proximity_analysis:
    nearest_deposits:
      - mineral_type: "rare_earth_elements"
        distance_km: 15.2
        deposit_name: "Mountain Pass Mine"
        source: "USGS_MRDS"
        confidence: 0.92
    proximity_score: 0.8  # 0-1 scale based on distance
    enrichment_potential: "high|medium|low"

# Geological Context Enhancement  
geological_formation:
  has_raw_value: "formation_name"
  geological_age: "period_era"
  rock_type: "igneous|sedimentary|metamorphic"
  source: "USGS_geological_map_api"

# Enhanced Environmental Enrichment
microclimate_data:
  temperature_variability: "seasonal_range_celsius"
  precipitation_seasonality: "wet_dry_season_pattern" 
  extreme_weather_frequency: "events_per_year"
  source: "weather_api_historical"

# Ecosystem Services
ecosystem_services:
  carbon_sequestration_potential: "tons_co2_per_hectare"
  biodiversity_index: "species_richness_estimate"
  water_regulation: "watershed_position"
  source: "ecosystem_services_api"
```

#### Infrastructure and Accessibility
```yaml
# Sample Accessibility
site_accessibility:
  nearest_road_km: 5.2
  elevation_change_to_road: 150  # meters
  terrain_difficulty: "easy|moderate|difficult"
  vehicle_access: "4wd_required|standard_vehicle|foot_only"

# Research Infrastructure Proximity  
research_infrastructure_nearby:
  field_stations:
    - name: "Station Name"
      distance_km: 12.5
      research_focus: ["ecology", "climate"]
  universities:
    - name: "University Name" 
      distance_km: 45.0
      relevant_departments: ["environmental_science"]
```

### 4. API Recommendations for Under-Populated Slots

#### High-Priority APIs for Enrichment

**Environmental Context APIs**
- **Global Land Cover Classification**: ESA CCI, MODIS, Copernicus
- **Soil Databases**: ISRIC SoilGrids, USDA SSURGO, FAO Digital Soil Map
- **Climate Data**: WorldClim, PRISM, ECMWF ERA5

**Geospatial Enhancement APIs**
- **Elevation**: USGS Elevation Point Query Service, Open-Elevation
- **Watersheds**: USGS Watershed Boundary Dataset API
- **Protected Areas**: World Database on Protected Areas API

**Ecological Context APIs**
- **Biodiversity**: GBIF Species Occurrence API, iNaturalist
- **Vegetation**: NDVI time series from NASA/MODIS
- **Land Use History**: Historical land cover change APIs

**Infrastructure and Human Impact APIs**
- **Population Density**: WorldPop, LandScan APIs
- **Transportation Networks**: OpenStreetMap Overpass API
- **Industrial Activities**: OpenStreetMap industrial features

#### Slot-Specific API Mapping

| Under-populated Slot | Recommended API | Enrichment Method |
|---------------------|-----------------|-------------------|
| `depth` | USGS/geological surveys | Estimated from geological context |
| `temp` | WorldClim, ERA5 | Historical climate normals |
| `ph` | SoilGrids | Soil pH predictions |
| `salinity` | Global soil salinity maps | Geospatial lookup |
| `growth_habit` | Plant trait databases | Species-based inference |
| `root_cond` | Root zone databases | Soil-climate correlation |

### 5. Critical Minerals Proximity Analysis

#### USGS 2022 Critical Minerals Integration
Implement proximity analysis for all 50 critical minerals:
- **Rare Earth Elements**: La, Ce, Pr, Nd, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Y, Sc
- **Strategic Metals**: Li, Co, Ni, PGMs (Pt, Pd, Rh, Ru, Ir, Os)
- **Technology Metals**: Ga, Ge, In, Te, REE for electronics
- **Energy Transition Materials**: Li, Co, Ni, Graphite, V

#### Implementation Framework
```python
# Pseudo-code for critical minerals analysis
def analyze_critical_minerals_proximity(lat, lon, search_radius_km=50):
    """
    Analyze proximity to critical mineral deposits.
    
    Data sources:
    - USGS Mineral Resources Data System (MRDS)
    - USGS National Minerals Information Center
    - State geological survey databases
    """
    nearby_deposits = query_usgs_mrds(lat, lon, search_radius_km)
    
    enrichment_factors = {
        'rare_earth_concentration': calculate_ree_potential(soil_geochemistry),
        'strategic_metal_indicators': analyze_geological_favorability(geology_api),
        'historical_mining_activity': query_historical_mining_data(lat, lon)
    }
    
    return {
        'critical_minerals_proximity': nearby_deposits,
        'enrichment_potential': enrichment_factors,
        'geological_context': get_geological_formation(lat, lon)
    }
```

### 6. Scalability and Performance Considerations

#### For Millions of Records
1. **Hierarchical Caching**: Regional → Country → Global level caches
2. **Batch Processing**: Geographic clustering for efficient API usage
3. **Intelligent Sampling**: Process representatives from similar environments
4. **Async Processing**: Parallel API calls with rate limiting
5. **Progressive Enhancement**: Core data first, detailed analysis second

#### Rate Limiting and API Management
```python
# Rate limiting framework
api_limits = {
    'usgs_elevation': 1000,   # per hour
    'weather_api': 10000,     # per day
    'soil_grids': 500,        # per hour
    'osm_overpass': 10000     # per day
}

# Intelligent batching
def batch_similar_locations(biosamples, cluster_radius_km=10):
    """Group nearby samples to minimize API calls."""
    return cluster_coordinates(biosamples, cluster_radius_km)
```

### 7. Quality Assurance Framework

#### Automated Quality Checks
1. **Coordinate Validation**: Flag impossible coordinates, elevation mismatches
2. **Temporal Consistency**: Verify collection dates vs. environmental data availability
3. **Ontological Consistency**: Check ENVO term relationships
4. **Cross-Source Validation**: Compare API results from multiple sources

#### Manual Review Triggers
- Confidence scores < 0.7
- Conflicts between asserted and API data
- Geographic outliers (samples far from expected environmental context)
- Missing critical enrichment data despite API availability

### 8. Implementation Phases

#### Phase 1: Foundation (Months 1-2)
- Extend crawl-first caching system for biosample-scale deployment
- Implement provenance tracking schema
- Create confidence scoring framework
- Build basic conflict detection

#### Phase 2: Core Enrichment (Months 3-4) 
- Integrate critical minerals proximity analysis
- Add geological context enrichment
- Implement ecosystem services APIs
- Create validation workflows

#### Phase 3: Scale and Optimize (Months 5-6)
- Deploy batch processing for large datasets
- Optimize API usage patterns
- Create quality assurance dashboards
- Build manual review interfaces

#### Phase 4: Community Integration (Months 7-8)
- Generate new slot recommendations for NMDC schema
- Create submission pipeline for enriched data
- Build visualization tools for enrichment results
- Develop community feedback mechanisms

### 9. Integration with Existing Infrastructure

#### MongoDB Enhancement
```javascript
// Enhanced document structure
{
  // Original NMDC data
  "asserted": { ... },
  
  // API enrichments with full provenance
  "inferred": {
    "soil_from_asserted_coords": { ... },
    "critical_minerals_proximity": { ... },
    "ecosystem_services": { ... }
  },
  
  // Quality metadata
  "enrichment_metadata": {
    "enrichment_date": "2024-08-21",
    "api_versions": { "usgs_mrds": "v2.1", "soilgrids": "v2.0" },
    "confidence_summary": { "high": 15, "medium": 8, "low": 2 },
    "validation_flags": ["coordinate_mismatch", "temporal_gap"]
  }
}
```

#### LinkML Schema Extensions
```yaml
# New slots for NMDC schema
CriticalMineralsProximity:
  description: "Analysis of proximity to critical mineral deposits"
  range: CriticalMineralsValue
  
CriticalMineralsValue:
  slots:
    - nearest_deposits
    - proximity_score  
    - enrichment_potential
    - geological_context
```

### 10. Success Metrics and Evaluation

#### Quantitative Metrics
- **Coverage Improvement**: Target 80% slot population (from current 22.7%)
- **API Success Rate**: >95% successful enrichment for records with coordinates
- **Validation Accuracy**: >90% agreement between high-confidence API data and expert review
- **Processing Throughput**: >1000 biosamples/hour with full enrichment

#### Qualitative Metrics
- **Scientific Value**: Community feedback on enrichment utility
- **Data Quality**: Expert assessment of enrichment accuracy
- **Usability**: Researcher adoption of enriched datasets
- **Reproducibility**: Consistent results across enrichment runs

## Conclusion

This strategy provides a roadmap for systematically enriching NMDC Biosample records through deterministic API integration. By building on the proven crawl-first architecture and extending it with robust provenance tracking, quality validation, and critical minerals analysis, we can transform under-populated biosample records into comprehensive environmental datasets suitable for advanced analysis and machine learning applications.

The approach balances scientific rigor with practical scalability, ensuring that enriched data maintains high quality while supporting the analysis of millions of biosample records across diverse environmental contexts.