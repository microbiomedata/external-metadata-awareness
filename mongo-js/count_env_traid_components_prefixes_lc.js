db.biosamples_env_triad_value_counts_gt_1.aggregate([
    { $unwind: "$components" },
    {
        $project: {
            prefix_lower: { $toLower: "$components.prefix" },
            count: "$count" // Use the top-level count
        }
    },
    {
        $group: {
            _id: "$prefix_lower",
            totalCount: { $sum: "$count" }
        }
    },
    { $sort: { totalCount: -1 } },
    { $out: "biosamples_env_triad_components_prefix_lc_counts" }
])
