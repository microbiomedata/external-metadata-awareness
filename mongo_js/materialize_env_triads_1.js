const start = new Date();

db.biosamples_flattened.aggregate([
    // Lookups
    {
        $lookup: {
            from: "biosamples_env_triad_value_counts_gt_1",
            localField: "env_broad_scale",
            foreignField: "env_triad_value",
            as: "env_broad_scale_matches"
        }
    },
    {
        $lookup: {
            from: "biosamples_env_triad_value_counts_gt_1",
            localField: "env_local_scale",
            foreignField: "env_triad_value",
            as: "env_local_scale_matches"
        }
    },
    {
        $lookup: {
            from: "biosamples_env_triad_value_counts_gt_1",
            localField: "env_medium",
            foreignField: "env_triad_value",
            as: "env_medium_matches"
        }
    },

    // Extract first match’s components or default to empty
    {
        $addFields: {
            broad_components: {
                $ifNull: [{$arrayElemAt: ["$env_broad_scale_matches.components", 0]}, []]
            },
            local_components: {
                $ifNull: [{$arrayElemAt: ["$env_local_scale_matches.components", 0]}, []]
            },
            medium_components: {
                $ifNull: [{$arrayElemAt: ["$env_medium_matches.components", 0]}, []]
            }
        }
    },

    // Skip documents with no valid components at all
    {
        $match: {
            $or: [
                {"broad_components.0": {$exists: true}},
                {"local_components.0": {$exists: true}},
                {"medium_components.0": {$exists: true}}
            ]
        }
    },

    // Build output with only populated fields
    {
        $project: {
            _id: 0,
            accession: 1,
            env_broad_scale: {
                $cond: [
                    {$gt: [{$size: "$broad_components"}, 0]},
                    {
                        value: "$env_broad_scale",
                        components: "$broad_components"
                    },
                    "$$REMOVE"
                ]
            },
            env_local_scale: {
                $cond: [
                    {$gt: [{$size: "$local_components"}, 0]},
                    {
                        value: "$env_local_scale",
                        components: "$local_components"
                    },
                    "$$REMOVE"
                ]
            },
            env_medium: {
                $cond: [
                    {$gt: [{$size: "$medium_components"}, 0]},
                    {
                        value: "$env_medium",
                        components: "$medium_components"
                    },
                    "$$REMOVE"
                ]
            }
        }
    },

    // Optional: enforce order
    {$sort: {accession: 1}},

    // Final write
    {$out: "env_triads"}
])

const end = new Date();
print("Elapsed time: " + (end - start) + " ms");

// Elapsed time: 1000367 ms
// ~ 17 minutes