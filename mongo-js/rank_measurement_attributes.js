// Comprehensive measurement-likeness ranking across NCBI, MIxS, and NMDC sources
// Combines empirical evidence with schema definitions to rank attributes by measurement potential

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting comprehensive measurement attribute ranking`);

// Drop output collection
db.measurement_attribute_rankings.drop();

print(`[${new Date().toISOString()}] Step 1: Gathering NCBI empirical evidence...`);

// Step 1: Get NCBI empirical evidence with format information
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
            avg_evidence_percentage: 1,
            format: { $arrayElemAt: ["$format_info.format", 0] },
            description: { $arrayElemAt: ["$format_info.description", 0] },
            synonyms: { $arrayElemAt: ["$format_info.synonyms", 0] },
            packages: { $arrayElemAt: ["$format_info.packages", 0] }
        }
    }
]).toArray();

print(`[${new Date().toISOString()}] Found ${ncbiEvidence.length} NCBI attributes with empirical evidence`);

print(`[${new Date().toISOString()}] Step 2: Gathering MIxS schema information...`);

// Step 2: Get MIxS slots with measurement-relevant information
const mixsSlots = db.global_mixs_slots.find({
    slot_name: { $exists: true, $ne: null }
}).toArray();

print(`[${new Date().toISOString()}] Found ${mixsSlots.length} MIxS slots`);

print(`[${new Date().toISOString()}] Step 3: Gathering NMDC schema information...`);

// Step 3: Get NMDC slots with measurement-relevant information
const nmdcSlots = db.global_nmdc_slots.find({
    name: { $exists: true, $ne: null }
}).toArray();

print(`[${new Date().toISOString()}] Found ${nmdcSlots.length} NMDC slots`);

print(`[${new Date().toISOString()}] Step 4: Analyzing and ranking attributes...`);

// Function to calculate measurement score based on multiple criteria
function calculateMeasurementScore(attr) {
    let score = 0;
    let factors = [];
    
    // NCBI Empirical Evidence (0-40 points)
    if (attr.unit_assertion_percentage !== undefined) {
        const unitScore = attr.unit_assertion_percentage * 20; // 0-20 points
        const mixedScore = attr.mixed_content_percentage * 20; // 0-20 points
        score += unitScore + mixedScore;
        factors.push(`unit_evidence=${unitScore.toFixed(1)}`);
        factors.push(`mixed_evidence=${mixedScore.toFixed(1)}`);
    }
    
    // Format Analysis (0-30 points)
    if (attr.format) {
        const format = attr.format.toLowerCase();
        if (format.includes('{float} {unit}') || format.includes('{integer} {unit}')) {
            score += 30;
            factors.push('explicit_unit_format=30');
        } else if (format.includes('{float}') || format.includes('{integer}')) {
            score += 20;
            factors.push('numeric_format=20');
        } else if (format.includes('unit')) {
            score += 15;
            factors.push('unit_mention=15');
        } else if (format.includes('{timestamp}')) {
            score += 5;
            factors.push('timestamp=5');
        }
    }
    
    // Range Analysis for MIxS/NMDC (0-25 points)
    if (attr.range) {
        const range = attr.range.toLowerCase();
        if (range.includes('quantityvalue') || range.includes('quantity')) {
            score += 25;
            factors.push('quantity_value_range=25');
        } else if (range.includes('float') || range.includes('double') || range.includes('decimal')) {
            score += 20;
            factors.push('numeric_range=20');
        } else if (range.includes('integer')) {
            score += 15;
            factors.push('integer_range=15');
        } else if (range.includes('string') && attr.expected_value && 
                   attr.expected_value.toLowerCase().includes('unit')) {
            score += 10;
            factors.push('string_with_unit_expected=10');
        }
    }
    
    // Name/Description Analysis (0-15 points)
    const name = (attr.name || attr.harmonized_name || '').toLowerCase();
    const description = (attr.description || attr.expected_value || '').toLowerCase();
    const combined = `${name} ${description}`;
    
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
        factors.push(`keywords=${keywordMatches.join(',')}`);
    }
    
    // Usage Volume Bonus (0-10 points)
    if (attr.total_attributes && attr.total_attributes > 1000) {
        const volumeScore = Math.min(Math.log10(attr.total_attributes) * 2, 10);
        score += volumeScore;
        factors.push(`volume_bonus=${volumeScore.toFixed(1)}`);
    }
    
    return {
        score: Math.round(score * 10) / 10, // Round to 1 decimal
        factors: factors
    };
}

// Process all attributes
const allAttributes = [];

// Process NCBI attributes
ncbiEvidence.forEach(attr => {
    const analysis = calculateMeasurementScore(attr);
    allAttributes.push({
        name: attr.harmonized_name,
        source: 'NCBI',
        measurement_score: analysis.score,
        scoring_factors: analysis.factors,
        
        // NCBI-specific data
        total_samples: attr.total_attributes || 0,
        unique_biosamples: attr.unique_biosamples_count || 0,
        unique_bioprojects: attr.unique_bioprojects_count || 0,
        unit_assertion_percentage: attr.unit_assertion_percentage || 0,
        mixed_content_percentage: attr.mixed_content_percentage || 0,
        format: attr.format || '',
        description: attr.description || '',
        synonyms: attr.synonyms || '',
        packages: attr.packages || '',
        
        // Schema fields (empty for NCBI)
        range: '',
        expected_value: '',
        pattern: '',
        
        analyzed_at: new Date()
    });
});

// Process MIxS slots
mixsSlots.forEach(slot => {
    const analysis = calculateMeasurementScore({
        name: slot.slot_name,
        range: slot.range,
        description: slot.description,
        expected_value: slot.examples ? slot.examples.map(ex => ex.value).join('; ') : ''
    });
    allAttributes.push({
        name: slot.slot_name,
        source: 'MIxS',
        measurement_score: analysis.score,
        scoring_factors: analysis.factors,
        
        // NCBI-specific data (empty for MIxS)
        total_samples: 0,
        unique_biosamples: 0,
        unique_bioprojects: 0,
        unit_assertion_percentage: 0,
        mixed_content_percentage: 0,
        format: '',
        synonyms: '',
        packages: '',
        
        // Schema fields
        range: slot.range || '',
        expected_value: slot.examples ? slot.examples.map(ex => ex.value).join('; ') : '',
        pattern: slot.structured_pattern ? slot.structured_pattern.syntax : '',
        description: slot.description || '',
        
        analyzed_at: new Date()
    });
});

// Process NMDC slots
nmdcSlots.forEach(slot => {
    const analysis = calculateMeasurementScore(slot);
    allAttributes.push({
        name: slot.name,
        source: 'NMDC',
        measurement_score: analysis.score,
        scoring_factors: analysis.factors,
        
        // NCBI-specific data (empty for NMDC)
        total_samples: 0,
        unique_biosamples: 0,
        unique_bioprojects: 0,
        unit_assertion_percentage: 0,
        mixed_content_percentage: 0,
        format: '',
        synonyms: '',
        packages: '',
        
        // Schema fields
        range: slot.range || '',
        expected_value: slot.expected_value || '',
        pattern: slot.pattern || '',
        description: slot.description || '',
        
        analyzed_at: new Date()
    });
});

print(`[${new Date().toISOString()}] Step 5: Inserting ranked results...`);

// Insert all attributes
if (allAttributes.length > 0) {
    db.measurement_attribute_rankings.insertMany(allAttributes);
}

// Create indexes
print(`[${new Date().toISOString()}] Creating indexes...`);
try {
    db.measurement_attribute_rankings.createIndex({measurement_score: -1}, {background: true});
    db.measurement_attribute_rankings.createIndex({source: 1}, {background: true});
    db.measurement_attribute_rankings.createIndex({name: 1}, {background: true});
} catch(e) {
    print(`Index creation warning: ${e.message}`);
}

const totalCount = db.measurement_attribute_rankings.countDocuments();
print(`[${new Date().toISOString()}] Inserted ${totalCount} ranked attributes`);

// Show top measurement-like attributes
print(`[${new Date().toISOString()}] Top 15 measurement-like attributes across all sources:`);
db.measurement_attribute_rankings.find().sort({measurement_score: -1}).limit(15).forEach(attr => {
    print(`  ${attr.measurement_score.toFixed(1)}: ${attr.name} (${attr.source}) - ${attr.scoring_factors.slice(0,3).join(', ')}`);
});

// Show distribution by source
print(`[${new Date().toISOString()}] Distribution by source:`);
db.measurement_attribute_rankings.aggregate([
    {$group: {
        _id: "$source",
        count: {$sum: 1},
        avg_score: {$avg: "$measurement_score"},
        max_score: {$max: "$measurement_score"}
    }},
    {$sort: {avg_score: -1}}
]).forEach(result => {
    print(`  ${result._id}: ${result.count} attributes, avg=${result.avg_score.toFixed(2)}, max=${result.max_score.toFixed(1)}`);
});

const endTime = new Date();
print(`[${endTime.toISOString()}] Completed in ${((endTime - startTime)/1000).toFixed(2)} seconds`);