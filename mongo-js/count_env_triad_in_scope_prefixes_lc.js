db.env_triad_component_in_scope_curies_lc.aggregate([
    {
        $project: {
            prefix_lower: {$toLower: "$prefix"},
            count: 1
        }
    },
    {
        $group: {
            _id: "$prefix_lower",
            totalCount: {$sum: "$count"}
        }
    },
    {
        $sort: {totalCount: -1}
    },
    {
        $out: "env_triad_in_scope_prefix_lc_counts"
    }
])