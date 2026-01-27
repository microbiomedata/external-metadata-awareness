// flatten_env_triads_multi_component.js
// Transforms env_triads collection into flattened multi-component relational structure
//
// Input: env_triads collection with nested components arrays
// Output: env_triads_flattened collection with one record per component
//
// Structure transformation:
// FROM: { accession: "X", env_broad_scale: { raw: "...", components: [{id: "A"}, {id: "B"}] } }
// TO:   [{ accession: "X", attribute: "env_broad_scale", instance: 0, id: "A", ... },
//        { accession: "X", attribute: "env_broad_scale", instance: 1, id: "B", ... }]

print('[' + new Date().toISOString() + '] Starting env_triads flattening transformation');

// Drop and recreate the flattened collection
db.env_triads_flattened.drop();
print('[' + new Date().toISOString() + '] Dropped existing env_triads_flattened collection');

// Get total count for progress tracking
const totalDocs = db.env_triads.countDocuments();
print('[' + new Date().toISOString() + '] Processing ' + totalDocs + ' documents from env_triads collection');

// Process in batches for memory efficiency
const batchSize = 1000;
let processed = 0;
let totalFlattened = 0;

// Use aggregation pipeline to flatten the structure
db.env_triads.aggregate([
    {
        $project: {
            accession: 1,
            env_broad_scale: 1,
            env_local_scale: 1,
            env_medium: 1
        }
    },
    {
        $addFields: {
            // Create array of all scale types with their data
            scale_data: [
                {
                    attribute: "env_broad_scale",
                    raw: "$env_broad_scale.raw",
                    components: { $ifNull: ["$env_broad_scale.components", []] }
                },
                {
                    attribute: "env_local_scale",
                    raw: "$env_local_scale.raw",
                    components: { $ifNull: ["$env_local_scale.components", []] }
                },
                {
                    attribute: "env_medium",
                    raw: "$env_medium.raw",
                    components: { $ifNull: ["$env_medium.components", []] }
                }
            ]
        }
    },
    {
        // Unwind scale_data to get one record per attribute type
        $unwind: "$scale_data"
    },
    {
        // Add component index for each component in the array
        $addFields: {
            "scale_data.components_with_index": {
                $map: {
                    input: { $range: [0, { $size: "$scale_data.components" }] },
                    as: "idx",
                    in: {
                        instance: "$$idx",
                        component: { $arrayElemAt: ["$scale_data.components", "$$idx"] }
                    }
                }
            }
        }
    },
    {
        // Unwind components to get one record per component instance
        // Include empty arrays to preserve raw values even when no components parsed
        $unwind: {
            path: "$scale_data.components_with_index",
            preserveNullAndEmptyArrays: true  // Keep empty component arrays
        }
    },
    {
        // Project final structure with both rawness levels
        $project: {
            _id: 0,
            accession: 1,
            attribute: "$scale_data.attribute",
            instance: { $ifNull: ["$scale_data.components_with_index.instance", 0] },
            // Both levels of "raw" data
            raw_original: "$scale_data.raw",  // Original from XML/biosample
            raw_component: { $ifNull: ["$scale_data.components_with_index.component.raw", null] },  // After splitting/parsing
            id: { $ifNull: ["$scale_data.components_with_index.component.id", null] },
            label: { $ifNull: ["$scale_data.components_with_index.component.label", null] },
            prefix: { $ifNull: ["$scale_data.components_with_index.component.prefix_uc", null] },
            source: { $ifNull: ["$scale_data.components_with_index.component.source", null] }
        }
    },
    {
        // Include all records: those with components AND those with only raw_original
        $match: {
            raw_original: { $exists: true, $ne: null, $ne: "" }
        }
    },
    {
        // Output to new collection
        $out: "env_triads_flattened"
    }
], { allowDiskUse: true });

// Get final count
const flattenedCount = db.env_triads_flattened.countDocuments();
print('[' + new Date().toISOString() + '] Flattening complete');
print('[' + new Date().toISOString() + '] Created ' + flattenedCount + ' flattened component records');
print('[' + new Date().toISOString() + '] Average components per biosample: ' + (flattenedCount / totalDocs).toFixed(2));

// Show sample of results
print('[' + new Date().toISOString() + '] Sample flattened records:');
db.env_triads_flattened.find().limit(3).forEach(doc => {
    print('  ' + doc.accession + ' | ' + doc.attribute + '[' + doc.instance + '] | ' +
          doc.id + ' | ' + doc.label + ' | ' + doc.source);
});

print('[' + new Date().toISOString() + '] env_triads flattening transformation completed');