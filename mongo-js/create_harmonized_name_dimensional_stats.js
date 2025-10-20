// Create harmonized_name_dimensional_stats from measurement_results_skip_filtered
//
// Aggregates quantulum3 parsing results to calculate dimensional vs dimensionless
// quantity statistics per harmonized_name.
//
// Input: measurement_results_skip_filtered collection (1.3M quantulum3 parse results)
// Output: harmonized_name_dimensional_stats collection (one doc per harmonized_name)
//
// Schema matches 3M DuckDB export for compatibility:
// - harmonized_name: field name
// - total_content_pairs: count of unique content values analyzed
// - total_quantities_found: quantities successfully parsed by quantulum3
// - dimensional_quantities: quantities with physical units (mass, length, temperature, etc.)
// - dimensionless_quantities: pure numbers, percentages, ratios
// - unique_content_with_any_units: unique content strings with any parseable units
// - unique_content_with_dimensional_units: unique content strings with dimensional units
// - unique_units_total: count of distinct unit strings
// - unique_dimensional_units: count of distinct dimensional unit strings
// - content_extraction_rate_pct: % of content that yielded quantities
// - dimensional_content_rate_pct: % of content with dimensional units
// - dimensional_of_extracted_pct: % of extracted quantities that are dimensional
// - analysis_timestamp: ISO timestamp of analysis run
//
// Note: Covers 351 harmonized_names (fields with parseable quantities after skip list filtering).
// See Issue #275 for comparison with 3M DuckDB version (432 fields, pre-skip-list).

print("[" + new Date().toISOString() + "] Starting dimensional stats analysis...");

// Dimensional entities (have physical dimensions)
const DIMENSIONAL_ENTITIES = [
    'acceleration', 'amount of substance', 'angle', 'area', 'capacitance',
    'catalytic activity', 'concentration', 'current', 'density', 'energy',
    'force', 'frequency', 'illuminance', 'inductance', 'length', 'luminosity',
    'magnetic flux', 'magnetic flux density', 'mass', 'molality', 'momentum',
    'power', 'pressure', 'radiation', 'radioactivity', 'resistance',
    'specific volume', 'speed', 'substance', 'temperature', 'time',
    'voltage', 'volume'
];

// Dimensionless entities
const DIMENSIONLESS_ENTITIES = [
    'dimensionless', 'count', 'fraction', 'percentage', 'ratio', 'unknown'
];

const analysisTimestamp = new Date().toISOString();

print("[" + new Date().toISOString() + "] Source collection: measurement_results_skip_filtered");
print("[" + new Date().toISOString() + "] Output collection: harmonized_name_dimensional_stats");

const totalDocs = db.measurement_results_skip_filtered.estimatedDocumentCount();
print("[" + new Date().toISOString() + "] Processing ~" + totalDocs.toLocaleString() + " measurement results...");

db.measurement_results_skip_filtered.aggregate([
    // Project needed fields
    {
        $project: {
            harmonized_name: 1,
            original_content: 1,
            entity: 1,
            unit: 1,
            is_dimensional: {
                $cond: {
                    if: { $in: [{ $toLower: { $ifNull: ["$entity", ""] } }, DIMENSIONAL_ENTITIES] },
                    then: true,
                    else: false
                }
            },
            has_unit: {
                $cond: {
                    if: { $and: [{ $ne: ["$unit", null] }, { $ne: ["$unit", ""] }] },
                    then: true,
                    else: false
                }
            }
        }
    },

    // Group by harmonized_name to collect sets and counts
    {
        $group: {
            _id: "$harmonized_name",
            // Collect unique content values
            unique_contents: { $addToSet: "$original_content" },
            unique_contents_with_units: {
                $addToSet: {
                    $cond: {
                        if: "$has_unit",
                        then: "$original_content",
                        else: "$$REMOVE"
                    }
                }
            },
            unique_contents_dimensional: {
                $addToSet: {
                    $cond: {
                        if: "$is_dimensional",
                        then: "$original_content",
                        else: "$$REMOVE"
                    }
                }
            },
            // Count quantities
            total_quantities: { $sum: 1 },
            dimensional_count: {
                $sum: { $cond: ["$is_dimensional", 1, 0] }
            },
            dimensionless_count: {
                $sum: { $cond: ["$is_dimensional", 0, 1] }
            },
            // Collect unique units
            unique_units: { $addToSet: "$unit" },
            unique_dimensional_units: {
                $addToSet: {
                    $cond: {
                        if: "$is_dimensional",
                        then: "$unit",
                        else: "$$REMOVE"
                    }
                }
            }
        }
    },

    // Calculate statistics
    {
        $project: {
            _id: 0,
            harmonized_name: "$_id",
            total_content_pairs: { $size: "$unique_contents" },
            total_quantities_found: "$total_quantities",
            dimensional_quantities: "$dimensional_count",
            dimensionless_quantities: "$dimensionless_count",
            unique_content_with_any_units: { $size: "$unique_contents_with_units" },
            unique_content_with_dimensional_units: { $size: "$unique_contents_dimensional" },
            unique_units_total: {
                $size: {
                    $filter: {
                        input: "$unique_units",
                        as: "unit",
                        cond: { $and: [{ $ne: ["$$unit", null] }, { $ne: ["$$unit", ""] }] }
                    }
                }
            },
            unique_dimensional_units: { $size: "$unique_dimensional_units" },
            // Store counts for percentage calculation
            _content_count: { $size: "$unique_contents" },
            _content_with_dimensional: { $size: "$unique_contents_dimensional" }
        }
    },

    // Add percentage calculations
    {
        $addFields: {
            content_extraction_rate_pct: {
                $round: [
                    {
                        $cond: {
                            if: { $gt: ["$_content_count", 0] },
                            then: {
                                $multiply: [
                                    { $divide: ["$total_quantities_found", "$_content_count"] },
                                    100
                                ]
                            },
                            else: 0
                        }
                    },
                    2
                ]
            },
            dimensional_content_rate_pct: {
                $round: [
                    {
                        $cond: {
                            if: { $gt: ["$_content_count", 0] },
                            then: {
                                $multiply: [
                                    { $divide: ["$_content_with_dimensional", "$_content_count"] },
                                    100
                                ]
                            },
                            else: 0
                        }
                    },
                    2
                ]
            },
            dimensional_of_extracted_pct: {
                $round: [
                    {
                        $cond: {
                            if: { $gt: ["$total_quantities_found", 0] },
                            then: {
                                $multiply: [
                                    { $divide: ["$dimensional_quantities", "$total_quantities_found"] },
                                    100
                                ]
                            },
                            else: 0
                        }
                    },
                    2
                ]
            },
            analysis_timestamp: analysisTimestamp
        }
    },

    // Remove temporary fields
    {
        $project: {
            _content_count: 0,
            _content_with_dimensional: 0
        }
    },

    // Sort by harmonized_name
    {
        $sort: { harmonized_name: 1 }
    },

    // Output to collection
    {
        $out: "harmonized_name_dimensional_stats"
    }
], { allowDiskUse: true });

// Generate summary statistics
const totalFields = db.harmonized_name_dimensional_stats.countDocuments();
const withDimensional = db.harmonized_name_dimensional_stats.countDocuments({ dimensional_quantities: { $gt: 0 } });
const onlyDimensionless = totalFields - withDimensional;

print("[" + new Date().toISOString() + "] ✅ Collection created successfully!");
print("");
print("Summary:");
print("  Total harmonized_names: " + totalFields.toLocaleString());
print("  With dimensional quantities: " + withDimensional.toLocaleString());
print("  Only dimensionless quantities: " + onlyDimensionless.toLocaleString());
print("  Analysis timestamp: " + analysisTimestamp);
print("");
print("Note: This collection covers harmonized_names with parseable quantities");
print("after skip list filtering (224 fields excluded). See Issue #275 for details.");

// Create index
print("[" + new Date().toISOString() + "] Creating index on harmonized_name...");
db.harmonized_name_dimensional_stats.createIndex({ harmonized_name: 1 }, { unique: true });
print("[" + new Date().toISOString() + "] ✅ Index created");
