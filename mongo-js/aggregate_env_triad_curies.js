db.biosamples_env_triad_value_counts_gt_1.aggregate([
    // Unwind the components array
    {$unwind: "$components"},

    // // Only consider components where either uses_obo_prefix or uses_bioportal_prefix is true
    // {
    //     $match: {
    //         $or: [
    //             {"components.uses_obo_prefix": true},
    //             {"components.uses_bioportal_prefix": true}
    //         ]
    //     }
    // },

    // Group by curie_uc, summing counts and retaining the prefix flags and prefix_uc
    {
        $group: {
            _id: "$components.curie_uc",
            count: {$sum: "$count"},
            uses_obo_prefix: {$first: "$components.uses_obo_prefix"},
            uses_bioportal_prefix: {$first: "$components.uses_bioportal_prefix"},
            prefix_uc: {$first: "$components.prefix_uc"}
        }
    },

    // Project the desired fields
    {
        $project: {
            curie_uc: "$_id",
            count: 1,
            uses_obo_prefix: 1,
            uses_bioportal_prefix: 1,
            prefix_uc: 1,
            _id: 0
        }
    },

    // Sort the documents by count in descending order
    {$sort: {count: -1}},

    // Output the aggregated documents into a new collection
    {$out: "env_triad_component_curies_uc"}
])
