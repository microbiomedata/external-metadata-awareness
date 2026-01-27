// Calculate measurement evidence ratios by joining count collections
// Input: harmonized_name_usage_stats + unit_assertion_counts + mixed_content_counts
// Output: measurement_evidence_ratios

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting measurement evidence ratios calculation`);

// Create beneficial indexes for join operations (error tolerant)
print(`[${new Date().toISOString()}] Ensuring beneficial indexes exist for joins`);
try {
    db.harmonized_name_usage_stats.createIndex({harmonized_name: 1}, {background: true});
} catch(e) {
    print(`harmonized_name_usage_stats.harmonized_name index exists: ${e.message}`);
}
try {
    db.unit_assertion_counts.createIndex({harmonized_name: 1}, {background: true});
} catch(e) {
    print(`unit_assertion_counts.harmonized_name index exists: ${e.message}`);
}
try {
    db.mixed_content_counts.createIndex({harmonized_name: 1}, {background: true});
} catch(e) {
    print(`mixed_content_counts.harmonized_name index exists: ${e.message}`);
}

// First get total attribute counts per harmonized_name
print(`[${new Date().toISOString()}] Counting total attributes per harmonized_name`);
db.biosamples_attributes.aggregate([
    {
        $group: {
            _id: "$harmonized_name",
            total_attributes: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            harmonized_name: "$_id",
            total_attributes: 1
        }
    },
    {
        $out: "temp_total_attributes"
    }
], { allowDiskUse: true });

// Aggregate unit_assertion_counts by harmonized_name (sum across all units)
print(`[${new Date().toISOString()}] Aggregating unit assertions by harmonized_name`);
db.unit_assertion_counts.aggregate([
    {
        $group: {
            _id: "$harmonized_name",
            attributes_with_units: { $sum: "$count" },
            unique_units: { $addToSet: "$unit" }
        }
    },
    {
        $project: {
            _id: 0,
            harmonized_name: "$_id",
            attributes_with_units: 1,
            unique_units_count: { $size: "$unique_units" }
        }
    },
    {
        $out: "temp_unit_totals"
    }
], { allowDiskUse: true });

// Drop output collection
db.measurement_evidence_percentages.drop();

// Join all collections to calculate true percentages
print(`[${new Date().toISOString()}] Joining collections and calculating evidence percentages`);
db.temp_total_attributes.aggregate([
    // Lookup unit assertion totals
    {
        $lookup: {
            from: "temp_unit_totals",
            localField: "harmonized_name",
            foreignField: "harmonized_name",
            as: "unit_data"
        }
    },
    
    // Lookup mixed content counts
    {
        $lookup: {
            from: "mixed_content_counts",
            localField: "harmonized_name",
            foreignField: "harmonized_name",
            as: "mixed_data"
        }
    },
    
    // Lookup biosample/bioproject usage stats
    {
        $lookup: {
            from: "harmonized_name_usage_stats",
            localField: "harmonized_name",
            foreignField: "harmonized_name",
            as: "usage_data"
        }
    },
    
    // Calculate evidence percentages
    {
        $project: {
            _id: 0,
            harmonized_name: 1,
            total_attributes: 1,
            
            // Get usage stats
            unique_biosamples_count: {
                $ifNull: [{ $arrayElemAt: ["$usage_data.unique_biosamples_count", 0] }, 0]
            },
            unique_bioprojects_count: {
                $ifNull: [{ $arrayElemAt: ["$usage_data.unique_bioprojects_count", 0] }, 0]
            },
            
            // Unit assertion metrics
            attributes_with_units: {
                $ifNull: [{ $arrayElemAt: ["$unit_data.attributes_with_units", 0] }, 0]
            },
            unique_units_count: {
                $ifNull: [{ $arrayElemAt: ["$unit_data.unique_units_count", 0] }, 0]
            },
            
            // Mixed content metrics  
            attributes_with_mixed_content: {
                $ifNull: [{ $arrayElemAt: ["$mixed_data.count", 0] }, 0]
            },
            
            // True percentages (0-1)
            unit_assertion_percentage: {
                $cond: {
                    if: { $gt: ["$total_attributes", 0] },
                    then: {
                        $divide: [
                            { $ifNull: [{ $arrayElemAt: ["$unit_data.attributes_with_units", 0] }, 0] },
                            "$total_attributes"
                        ]
                    },
                    else: 0
                }
            },
            
            mixed_content_percentage: {
                $cond: {
                    if: { $gt: ["$total_attributes", 0] },
                    then: {
                        $divide: [
                            { $ifNull: [{ $arrayElemAt: ["$mixed_data.count", 0] }, 0] },
                            "$total_attributes"
                        ]
                    },
                    else: 0
                }
            },
            
            // Average evidence percentage (average of both percentages)
            avg_evidence_percentage: {
                $divide: [
                    {
                        $add: [
                            {
                                $cond: {
                                    if: { $gt: ["$total_attributes", 0] },
                                    then: {
                                        $divide: [
                                            { $ifNull: [{ $arrayElemAt: ["$unit_data.attributes_with_units", 0] }, 0] },
                                            "$total_attributes"
                                        ]
                                    },
                                    else: 0
                                }
                            },
                            {
                                $cond: {
                                    if: { $gt: ["$total_attributes", 0] },
                                    then: {
                                        $divide: [
                                            { $ifNull: [{ $arrayElemAt: ["$mixed_data.count", 0] }, 0] },
                                            "$total_attributes"
                                        ]
                                    },
                                    else: 0
                                }
                            }
                        ]
                    },
                    2
                ]
            }
        }
    },
    
    // Sort by average evidence percentage descending
    {
        $sort: { avg_evidence_percentage: -1 }
    },
    
    {
        $out: "measurement_evidence_percentages"
    }
], { allowDiskUse: true });

// Clean up temporary collections
db.temp_total_attributes.drop();
db.temp_unit_totals.drop();

// Create indexes on output collection for efficient querying
print(`[${new Date().toISOString()}] Creating indexes on output collection`);
try {
    db.measurement_evidence_percentages.createIndex({harmonized_name: 1}, {background: true});
} catch(e) {
    print(`Output harmonized_name index exists: ${e.message}`);
}
try {
    db.measurement_evidence_percentages.createIndex({avg_evidence_percentage: -1}, {background: true});
} catch(e) {
    print(`Output avg_evidence_percentage index exists: ${e.message}`);
}
try {
    db.measurement_evidence_percentages.createIndex({unit_assertion_percentage: -1}, {background: true});
} catch(e) {
    print(`Output unit_percentage index exists: ${e.message}`);
}
try {
    db.measurement_evidence_percentages.createIndex({mixed_content_percentage: -1}, {background: true});
} catch(e) {
    print(`Output mixed_percentage index exists: ${e.message}`);
}

const resultCount = db.measurement_evidence_percentages.countDocuments();
print(`[${new Date().toISOString()}] Created ${resultCount} measurement evidence percentage records`);

// Show top 10 by average evidence percentage
print(`[${new Date().toISOString()}] Top 10 harmonized_names by average evidence percentage:`);
db.measurement_evidence_percentages.find().limit(10).forEach(doc => {
    print(`  ${doc.harmonized_name}: avg=${(doc.avg_evidence_percentage*100).toFixed(1)}%, unit%=${(doc.unit_assertion_percentage*100).toFixed(1)}%, mixed%=${(doc.mixed_content_percentage*100).toFixed(1)}%`);
});

const endTime = new Date();
print(`[${endTime.toISOString()}] Completed in ${((endTime - startTime)/1000).toFixed(2)} seconds`);