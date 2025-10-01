# Measurement Value and Unit Extraction Strategies

*Date: 2025-09-28*  
*Context: Post-measurement discovery pipeline implementation*

## Problem Statement

After identifying harmonized attribute names most likely to contain measurements, the next challenge is efficiently and accurately extracting clean values and standardized units from biomedical and environmental metagenome samples.

**Current Challenge with quantulum3:**
- Computationally expensive
- Successfully separates values from units
- Reduces unit expression variability
- **Major Issue**: Often produces nonsensical inferences for domain-specific units

## Enhanced Prioritization Strategies

### 1. Domain Knowledge Overlay

**Approach**: Create biomedical/environmental unit dictionaries and apply domain-specific scoring.

**Implementation Strategy:**
```python
biomedical_units = {
    'temperature': ['°C', 'celsius', 'C', 'F', 'fahrenheit', 'K', 'kelvin'],
    'mass': ['g', 'kg', 'mg', 'μg', 'grams', 'kilograms', 'milligrams'],
    'time': ['days', 'd', 'weeks', 'w', 'months', 'mo', 'years', 'y', 'yr'],
    'volume': ['mL', 'L', 'μL', 'milliliters', 'liters'],
    'concentration': ['ppm', 'ppb', 'mg/L', 'g/L', 'M', 'mM', 'μM']
}

environmental_units = {
    'depth': ['m', 'meters', 'cm', 'centimeters', 'ft', 'feet', 'km'],
    'salinity': ['ppt', 'ppm', 'PSU', '‰'],
    'pH': ['pH', 'pH units', ''],  # pH often unitless
    'conductivity': ['μS/cm', 'mS/cm', 'S/m'],
    'pressure': ['bar', 'atm', 'Pa', 'kPa', 'MPa', 'psi']
}
```

**Benefits:**
- Boost scores for harmonized names frequently appearing with known domain units
- Penalize fields containing obvious non-measurements
- Domain-aware confidence scoring

### 2. Value Distribution Analysis

**Concept**: Analyze numeric patterns to identify likely measurement fields based on statistical properties.

**Key Indicators:**
- **Narrow, reasonable ranges**: `host_age` values 20-80 (likely days) vs 20,000+ (probably something else)
- **Coefficient of variation**: High CV might indicate mixed content types
- **Range consistency**: Measurements typically have bounded, logical ranges

**Implementation Example:**
```javascript
// Statistical profiling of numeric content
db.biosamples_attributes.aggregate([
    {$match: {harmonized_name: "host_age"}},
    {$project: {
        numeric_value: {
            $toDouble: {
                $arrayElemAt: [
                    {$regexFindAll: {input: "$content", regex: /\d+\.?\d*/}}, 0
                ]
            }
        }
    }},
    {$group: {
        _id: null,
        avg: {$avg: "$numeric_value"},
        min: {$min: "$numeric_value"},
        max: {$max: "$numeric_value"},
        stddev: {$stdDevPop: "$numeric_value"}
    }}
])
```

### 3. Unit Consensus Scoring

**Strategy**: Evaluate measurement reliability based on unit consistency within harmonized names.

**Scoring Criteria:**
- **High confidence**: 80%+ of unit assertions are the same unit
- **Medium confidence**: 60-80% consensus on dominant unit
- **Low confidence**: Highly fragmented units requiring careful handling

**Benefits:**
- Identifies fields with reliable, consistent measurement patterns
- Flags fields needing special handling or manual review
- Reduces processing time by focusing on high-confidence fields

## Efficient Value/Unit Extraction Approaches

### 1. Tiered Regex Approach

**Philosophy**: Fast first-pass with domain-specific patterns, avoiding expensive NLP where possible.

**Biomedical Patterns:**
```python
biomedical_patterns = [
    # Temporal measurements
    r'(\d+\.?\d*)\s*(days?|d|weeks?|w|months?|mo|years?|y|yr)',
    
    # Mass measurements
    r'(\d+\.?\d*)\s*(g|kg|mg|μg|grams?|kilograms?|milligrams?)',
    
    # Temperature measurements
    r'(\d+\.?\d*)\s*(°C|celsius|C|°F|fahrenheit|F|K|kelvin)',
    
    # Volume measurements
    r'(\d+\.?\d*)\s*(mL|L|μL|ml|l|milliliters?|liters?)',
    
    # Concentration measurements
    r'(\d+\.?\d*)\s*(ppm|ppb|mg/L|g/L|M|mM|μM)'
]
```

**Environmental Patterns:**
```python
environmental_patterns = [
    # Depth/distance measurements
    r'(\d+\.?\d*)\s*(m|meters?|cm|centimeters?|ft|feet|km|kilometers?)',
    
    # Salinity measurements
    r'(\d+\.?\d*)\s*(ppt|ppm|PSU|‰)',
    
    # pH measurements (often unitless)
    r'pH\s*(\d+\.?\d*)|(\d+\.?\d*)\s*pH',
    
    # Conductivity measurements
    r'(\d+\.?\d*)\s*(μS/cm|mS/cm|S/m)',
    
    # Pressure measurements
    r'(\d+\.?\d*)\s*(bar|atm|Pa|kPa|MPa|psi)'
]
```

**Performance Benefits:**
- Processes ~80% of common patterns with minimal computation
- Domain-specific accuracy higher than general NLP approaches
- Easily maintainable and extensible

### 2. Hybrid Strategy

**Architecture**: Combine fast regex processing with selective NLP fallback.

**Workflow:**
1. **Fast Pass**: Apply domain-specific regex patterns
2. **Pattern Matching**: ~80% of cases resolved quickly
3. **NLP Fallback**: Use quantulum3 only for unmatched cases
4. **Confidence Scoring**: Domain-specific validation of all results

**Implementation Strategy:**
```python
def extract_measurement(content, harmonized_name):
    # Fast domain-specific extraction
    fast_result = apply_domain_patterns(content, harmonized_name)
    
    if fast_result.confidence > 0.8:
        return fast_result
    
    # Expensive NLP fallback for difficult cases
    nlp_result = quantulum3.parse(content)
    return merge_results(fast_result, nlp_result, harmonized_name)
```

### 3. Environmental Domain Approach

**Specialized Handling for Environmental Measurements:**

**pH Measurements:**
- Range: Almost always 0-14
- Unit: Often missing or implicit
- Pattern: `pH 7.2`, `7.2 pH`, or just `7.2` in pH context

**Temperature Measurements:**
- Environmental range: -50°C to +70°C typically
- Common units: °C, F, K
- Context clues: `temp`, `temperature` in harmonized name

**Depth Measurements:**
- Geological context: meters/feet with reasonable ranges
- Marine: 0-11,000m typical
- Terrestrial: 0-100m typical for sampling

**Salinity Measurements:**
- Marine range: 30-40 ppt typical
- Freshwater: 0-1 ppt
- Units: ppt, ppm, PSU

### 4. Measurement Context Clues

**Semantic Harmonized Name Analysis:**

**High Confidence Mappings:**
- `samp_store_temp` → temperature measurement (°C most likely)
- `host_age` → temporal measurement (days/weeks/months)
- `depth` → distance measurement (meters/feet)
- `pH` → pH measurement (unitless, 0-14 range)
- `salinity` → salinity measurement (ppt/ppm)

**Medium Confidence:**
- `size` → could be length, area, volume, mass
- `concentration` → needs unit context for interpretation
- `pressure` → various units possible

**Benefits:**
- Constrains unit expectations based on semantic meaning
- Reduces false positive unit assignments
- Enables domain-specific validation rules

## Specific Implementation Ideas for Current Pipeline

### 1. Unit Frequency Analysis Target

**Purpose**: Analyze unit distribution within high-scoring harmonized names.

**MongoDB Aggregation:**
```javascript
// For each promising harmonized_name, analyze unit frequency
db.unit_assertion_counts.aggregate([
    {$match: {harmonized_name: {$in: ["depth", "host_age", "temperature", "pH"]}}},
    {$group: {
        _id: "$harmonized_name",
        total_assertions: {$sum: "$count"},
        units: {$push: {unit: "$unit", count: "$count"}}
    }},
    {$project: {
        harmonized_name: "$_id",
        total_assertions: 1,
        dominant_unit: {$arrayElemAt: ["$units", 0]},
        unit_diversity: {$size: "$units"},
        units: 1
    }}
])
```

### 2. Value Range Profiling Target

**Purpose**: Extract and analyze numeric value distributions for measurement validation.

**Implementation:**
```javascript
// Statistical analysis of numeric values per harmonized name
db.biosamples_attributes.aggregate([
    {$match: {harmonized_name: "depth"}},
    {$project: {
        harmonized_name: 1,
        content: 1,
        numeric_matches: {$regexFindAll: {input: "$content", regex: /\d+\.?\d*/}}
    }},
    {$unwind: "$numeric_matches"},
    {$project: {
        harmonized_name: 1,
        numeric_value: {$toDouble: "$numeric_matches.match"}
    }},
    {$group: {
        _id: "$harmonized_name",
        count: {$sum: 1},
        avg: {$avg: "$numeric_value"},
        min: {$min: "$numeric_value"},
        max: {$max: "$numeric_value"},
        stddev: {$stdDevPop: "$numeric_value"}
    }}
])
```

### 3. Pattern-Based Confidence Scoring

**Confidence Levels:**

**High Confidence (0.9+):**
- `"25 °C"` - explicit unit with space
- `"1.5 meters"` - spelled-out unit
- `"pH 7.2"` - domain-specific format

**Medium Confidence (0.6-0.9):**
- `"25C"` - implicit unit, common abbreviation
- `"1.5m"` - abbreviated unit, no space
- `"7.2"` - numeric only in pH context

**Low Confidence (0.3-0.6):**
- `"warm"` - qualitative descriptor
- `"deep"` - relative measurement
- `"acidic"` - qualitative chemical property

**Very Low Confidence (<0.3):**
- Mixed units in same field
- Non-numeric content
- Obvious measurement errors

## Recommended Implementation Priority

### Phase 1: Quick Wins
1. **Unit frequency analysis** for top measurement-evidence fields
2. **Domain-specific regex patterns** for common cases
3. **Range validation** for numeric values

### Phase 2: Enhanced Processing
1. **Hybrid regex + NLP approach**
2. **Confidence scoring system**
3. **Semantic harmonized name analysis**

### Phase 3: Optimization
1. **Performance profiling** of extraction methods
2. **Domain knowledge integration**
3. **Automated quality assessment**

## Success Metrics

### Accuracy Metrics
- **Unit standardization rate**: % of successfully normalized units
- **Value extraction accuracy**: Comparison with manual validation
- **Domain appropriateness**: Units make sense for measurement type

### Efficiency Metrics
- **Processing speed**: Records per second
- **Regex vs NLP ratio**: % resolved without expensive processing
- **Confidence distribution**: How many high-confidence extractions

### Coverage Metrics
- **Measurement field coverage**: % of likely measurement fields processed
- **Unit diversity captured**: Comprehensive unit vocabulary
- **Edge case handling**: Success rate on unusual formats

---

*This analysis provides a roadmap for moving from measurement field identification to practical value and unit extraction for biomedical and environmental metagenome data.*