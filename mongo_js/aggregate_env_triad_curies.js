db.biosamples_env_triad_value_counts_gt_1.aggregate([
    // Unwind the components array
    {$unwind: "$components"},

    // Only consider components where either uses_obo_prefix or uses_bioportal_prefix is true
    {
        $match: {
            $or: [
                {"components.uses_obo_prefix": true},
                {"components.uses_bioportal_prefix": true}
            ]
        }
    },

    // Group by the prefix and local fields, summing counts and retaining the prefix flags
    {
        $group: {
            _id: {prefix: "$components.prefix", local: "$components.local"},
            count: {$sum: "$count"},
            uses_obo_prefix: {$first: "$components.uses_obo_prefix"},
            uses_bioportal_prefix: {$first: "$components.uses_bioportal_prefix"}
        }
    },

    // Compute the curie_lc field, e.g., "envo:00002003"
    {
        $addFields: {
            curie_lc: {$concat: [{$toLower: "$_id.prefix"}, ":", "$_id.local"]}
        }
    },

    // Project the desired fields
    {
        $project: {
            curie_lc: 1,
            count: 1,
            uses_obo_prefix: 1,
            uses_bioportal_prefix: 1,
            _id: 0
        }
    },

    // Sort the documents by count in descending order
    {$sort: {count: -1}},

    // Output the aggregated documents into a new collection
    {$out: "env_triad_component_in_scope_curies_lc"}
])
