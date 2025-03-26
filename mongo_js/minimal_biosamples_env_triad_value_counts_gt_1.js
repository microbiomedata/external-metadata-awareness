db.biosamples_flattened.aggregate([
    {
        $project: {
            env_values: [
                "$env_broad_scale",
                "$env_local_scale",
                "$env_medium"
            ]
        }
    },
    {
        $unwind: "$env_values"
    },
    {
        $match: {
            env_values: {
                $nin: [null, "missing", "not determined"]
            }
        }
    },
    {
        $group: {
            _id: "$env_values",
            count: {$sum: 1}
        }
    },
    {
        $match: {
            count: {$gte: 2}
        }
    },
    {
        $project: {
            _id: 0,
            env_triad_value: "$_id",
            count: 1
        }
    },
    {
        $sort: {count: -1}
    },
    {
        $out: "biosamples_env_triad_value_counts_gt_1"
    }
])

