db.biosamples_env_triad_value_counts_gt_1.aggregate([
    // Unwind the components array so each component is processed individually
    {$unwind: "$components"},

    // Group by the unique label from components, summing count and capturing lingering_envo and digits_only
    {
        $group: {
            _id: "$components.label",
            count: {$sum: "$count"},
            lingering_envo: {$first: "$components.lingering_envo"},
            digits_only: {$first: "$components.digits_only"}
        }
    },

    // Compute the label length, using $ifNull to default null labels to an empty string
    {
        $addFields: {
            label_length: {$strLenCP: {$ifNull: ["$_id", ""]}}
        }
    },

    // Project fields in the desired format
    {
        $project: {
            label: "$_id",
            count: 1,
            lingering_envo: 1,
            digits_only: 1,
            label_length: 1,
            _id: 0
        }
    },

    // Sort by count in descending order
    {$sort: {count: -1}},

    // Output the results into a new collection
    {$out: "env_triad_component_labels"}
])
