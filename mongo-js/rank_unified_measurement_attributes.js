// Unified measurement-likeness ranking that consolidates attributes across NCBI, MIxS, and NMDC sources
// Combines empirical evidence with schema definitions for the same attribute name

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting unified measurement attribute ranking`);

// Drop output collection
db.unified_measurement_attribute_rankings.drop();

print(`[${new Date().toISOString()}] Step 1: Gathering all attribute data by name...`);

// Step 1: Collect all data sources into a unified view by attribute name
const attributeData = new Map();

// Get NCBI empirical evidence
print(`[${new Date().toISOString()}] Processing NCBI empirical evidence...`);
const ncbiEvidence = db.measurement_evidence_percentages.aggregate([
    {
        $lookup: {
            from: "ncbi_attributes_flattened",
            localField: "harmonized_name",
            foreignField: "harmonized_name",
            as: "format_info"
        }
    },
    {
        $project: {
            harmonized_name: 1,
            total_attributes: 1,
            unique_biosamples_count: 1,
            unique_bioprojects_count: 1,
            unit_assertion_percentage: 1,
            mixed_content_percentage: 1,
            format: { $arrayElemAt: ["$format_info.format", 0] },
            description: { $arrayElemAt: ["$format_info.description", 0] },
            synonyms: { $arrayElemAt: ["$format_info.synonyms", 0] },
            packages: { $arrayElemAt: ["$format_info.packages", 0] }
        }
    }
]).toArray();

ncbiEvidence.forEach(attr => {
    const name = attr.harmonized_name;
    if (!attributeData.has(name)) {
        attributeData.set(name, {
            name: name,
            sources: [],
            // NCBI empirical data
            total_samples: 0,
            unique_biosamples: 0,
            unique_bioprojects: 0,
            unit_assertion_percentage: 0,
            mixed_content_percentage: 0,
            // Schema information
            formats: [],
            ranges: [],
            descriptions: [],
            patterns: [],
            synonyms: '',
            packages: ''
        });
    }
    
    const attrData = attributeData.get(name);
    attrData.sources.push('NCBI');
    attrData.total_samples = attr.total_attributes || 0;
    attrData.unique_biosamples = attr.unique_biosamples_count || 0;
    attrData.unique_bioprojects = attr.unique_bioprojects_count || 0;
    attrData.unit_assertion_percentage = attr.unit_assertion_percentage || 0;
    attrData.mixed_content_percentage = attr.mixed_content_percentage || 0;
    
    if (attr.format) attrData.formats.push(`NCBI: ${attr.format}`);
    if (attr.description) attrData.descriptions.push(`NCBI: ${attr.description}`);
    if (attr.synonyms) attrData.synonyms = attr.synonyms;
    if (attr.packages) attrData.packages = attr.packages;
});

print(`[${new Date().toISOString()}] Processed ${ncbiEvidence.length} NCBI attributes`);

// Get MIxS schema data
print(`[${new Date().toISOString()}] Processing MIxS schema data...`);
const mixsSlots = db.global_mixs_slots.find({
    slot_name: { $exists: true, $ne: null }
}).toArray();

mixsSlots.forEach(slot => {
    const name = slot.slot_name;
    if (!attributeData.has(name)) {
        attributeData.set(name, {
            name: name,
            sources: [],
            total_samples: 0,
            unique_biosamples: 0,
            unique_bioprojects: 0,
            unit_assertion_percentage: 0,
            mixed_content_percentage: 0,
            formats: [],
            ranges: [],
            descriptions: [],
            patterns: [],
            synonyms: '',
            packages: ''
        });
    }
    
    const attrData = attributeData.get(name);
    attrData.sources.push('MIxS');
    
    if (slot.range) attrData.ranges.push(`MIxS: ${slot.range}`);
    if (slot.description) attrData.descriptions.push(`MIxS: ${slot.description}`);
    if (slot.structured_pattern && slot.structured_pattern.syntax) {
        attrData.patterns.push(`MIxS: ${slot.structured_pattern.syntax}`);
    }
});

print(`[${new Date().toISOString()}] Processed ${mixsSlots.length} MIxS slots`);

// Get NMDC schema data
print(`[${new Date().toISOString()}] Processing NMDC schema data...`);
const nmdcSlots = db.global_nmdc_slots.find({
    name: { $exists: true, $ne: null }
}).toArray();

nmdcSlots.forEach(slot => {
    const name = slot.name;
    if (!attributeData.has(name)) {
        attributeData.set(name, {
            name: name,
            sources: [],
            total_samples: 0,
            unique_biosamples: 0,
            unique_bioprojects: 0,
            unit_assertion_percentage: 0,
            mixed_content_percentage: 0,
            formats: [],
            ranges: [],
            descriptions: [],
            patterns: [],
            synonyms: '',
            packages: ''
        });
    }
    
    const attrData = attributeData.get(name);
    attrData.sources.push('NMDC');
    
    if (slot.range) attrData.ranges.push(`NMDC: ${slot.range}`);
    if (slot.description) attrData.descriptions.push(`NMDC: ${slot.description}`);
});

print(`[${new Date().toISOString()}] Processed ${nmdcSlots.length} NMDC slots`);

print(`[${new Date().toISOString()}] Step 2: Calculating unified measurement scores...`);

// Function to calculate unified measurement score
function calculateUnifiedMeasurementScore(attr) {
    let score = 0;
    let factors = [];
    
    // NCBI Empirical Evidence (0-40 points) - HIGHEST WEIGHT
    if (attr.unit_assertion_percentage > 0 || attr.mixed_content_percentage > 0) {
        const unitScore = attr.unit_assertion_percentage * 25; // 0-25 points (increased weight)
        const mixedScore = attr.mixed_content_percentage * 15; // 0-15 points
        score += unitScore + mixedScore;
        factors.push(`empirical_evidence=${(unitScore + mixedScore).toFixed(1)}`);
        if (attr.unit_assertion_percentage > 0) factors.push(`unit_assertions=${(attr.unit_assertion_percentage*100).toFixed(1)}%`);
        if (attr.mixed_content_percentage > 0) factors.push(`mixed_content=${(attr.mixed_content_percentage*100).toFixed(1)}%`);
    }
    
    // Multi-source Schema Consistency Bonus (0-15 points)
    const sourceCount = attr.sources.length;
    if (sourceCount > 1) {
        const consistencyBonus = Math.min(sourceCount * 5, 15);
        score += consistencyBonus;
        factors.push(`multi_source_consistency=${consistencyBonus}(${attr.sources.join(',')})`);
    }
    
    // Format Analysis (0-25 points)
    const allFormats = (attr.formats || []).join(' ').toLowerCase();
    const allRanges = (attr.ranges || []).join(' ').toLowerCase();
    
    if (allFormats.includes('{float} {unit}') || allFormats.includes('{integer} {unit}')) {
        score += 25;
        factors.push('explicit_unit_format=25');
    } else if (allRanges.includes('quantityvalue')) {
        score += 20;
        factors.push('quantity_value_range=20');
    } else if (allFormats.includes('{float}') || allFormats.includes('{integer}') || allRanges.includes('float') || allRanges.includes('integer')) {
        score += 15;
        factors.push('numeric_format=15');
    } else if (allFormats.includes('unit') || allRanges.includes('unit')) {
        score += 10;
        factors.push('unit_mention=10');
    }
    
    // Name/Description Analysis (0-15 points)
    const name = (attr.name || '').toLowerCase();
    const allDescriptions = (attr.descriptions || []).join(' ').toLowerCase();
    const combined = `${name} ${allDescriptions}`;
    
    const measurementKeywords = [
        'temperature', 'depth', 'height', 'weight', 'mass', 'volume', 'length',
        'concentration', 'ph', 'salinity', 'pressure', 'density', 'conductivity',
        'turbidity', 'moisture', 'humidity', 'speed', 'rate', 'flow', 'flux',
        'diameter', 'size', 'area', 'distance', 'thickness', 'width', 'age',
        'amount', 'count', 'number', 'quantity', 'level', 'content', 'percent'
    ];
    
    const keywordMatches = measurementKeywords.filter(kw => combined.includes(kw));
    if (keywordMatches.length > 0) {
        const keywordScore = Math.min(keywordMatches.length * 3, 15);
        score += keywordScore;
        factors.push(`keywords=${keywordMatches.slice(0,5).join(',')}`);
    }
    
    // Usage Volume Bonus (0-10 points)
    if (attr.total_samples && attr.total_samples > 1000) {
        const volumeScore = Math.min(Math.log10(attr.total_samples) * 2, 10);
        score += volumeScore;
        factors.push(`volume_bonus=${volumeScore.toFixed(1)}`);
    }
    
    return {
        score: Math.round(score * 10) / 10,
        factors: factors
    };
}

// Process all unified attributes
const unifiedAttributes = [];
let ncbiOnlyCount = 0;
let mixsOnlyCount = 0;
let nmdcOnlyCount = 0;
let multiSourceCount = 0;

for (const [name, attrData] of attributeData) {
    const analysis = calculateUnifiedMeasurementScore(attrData);
    
    // Count source combinations
    if (attrData.sources.length === 1) {
        if (attrData.sources[0] === 'NCBI') ncbiOnlyCount++;
        else if (attrData.sources[0] === 'MIxS') mixsOnlyCount++;
        else if (attrData.sources[0] === 'NMDC') nmdcOnlyCount++;
    } else {
        multiSourceCount++;
    }
    
    unifiedAttributes.push({
        name: name,
        sources: attrData.sources,
        source_count: attrData.sources.length,
        measurement_score: analysis.score,
        scoring_factors: analysis.factors,
        
        // NCBI empirical data
        total_samples: attrData.total_samples,
        unique_biosamples: attrData.unique_biosamples,
        unique_bioprojects: attrData.unique_bioprojects,
        unit_assertion_percentage: attrData.unit_assertion_percentage,
        mixed_content_percentage: attrData.mixed_content_percentage,
        
        // Schema information
        formats: attrData.formats,
        ranges: attrData.ranges,
        descriptions: attrData.descriptions.slice(0, 3), // Limit for size
        patterns: attrData.patterns,
        synonyms: attrData.synonyms,
        packages: attrData.packages,
        
        analyzed_at: new Date()
    });
}

print(`[${new Date().toISOString()}] Step 3: Inserting unified results...`);

// Insert all unified attributes
if (unifiedAttributes.length > 0) {
    db.unified_measurement_attribute_rankings.insertMany(unifiedAttributes);
}

// Create indexes
print(`[${new Date().toISOString()}] Creating indexes...`);
try {
    db.unified_measurement_attribute_rankings.createIndex({measurement_score: -1}, {background: true});
    db.unified_measurement_attribute_rankings.createIndex({name: 1}, {background: true});
    db.unified_measurement_attribute_rankings.createIndex({source_count: -1}, {background: true});
} catch(e) {
    print(`Index creation warning: ${e.message}`);
}

const totalCount = db.unified_measurement_attribute_rankings.countDocuments();
print(`[${new Date().toISOString()}] Inserted ${totalCount} unified attribute rankings`);

// Summary statistics
print(`[${new Date().toISOString()}] Source Distribution:`);
print(`  NCBI only: ${ncbiOnlyCount}`);
print(`  MIxS only: ${mixsOnlyCount}`);
print(`  NMDC only: ${nmdcOnlyCount}`);
print(`  Multi-source: ${multiSourceCount}`);

// Show top measurement-like attributes
print(`[${new Date().toISOString()}] Top 15 unified measurement-like attributes:`);
db.unified_measurement_attribute_rankings.find().sort({measurement_score: -1}).limit(15).forEach(attr => {
    const sourceList = attr.sources.join('+');
    print(`  ${attr.measurement_score.toFixed(1)}: ${attr.name} (${sourceList}) - ${attr.scoring_factors.slice(0,3).join(', ')}`);
});

const endTime = new Date();
print(`[${endTime.toISOString()}] Completed unified analysis in ${((endTime - startTime)/1000).toFixed(2)} seconds`);