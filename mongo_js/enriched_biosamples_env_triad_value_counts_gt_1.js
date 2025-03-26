// < 4 minutes

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
            _id: {$toString: "$env_values"},
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
            count: 1,
            length: {$strLenCP: "$_id"},
            envo_count: {
                $let: {
                    vars: {
                        lower: {$toLower: "$_id"},
                        target: "envo"
                    },
                    in: {
                        $floor: {
                            $divide: [
                                {
                                    $subtract: [
                                        {$strLenCP: "$$lower"},
                                        {
                                            $strLenCP: {
                                                $replaceAll: {
                                                    input: "$$lower",
                                                    find: "$$target",
                                                    replacement: ""
                                                }
                                            }
                                        }
                                    ]
                                },
                                {$strLenCP: "$$target"}
                            ]
                        }
                    }
                }
            },
            digits_only: {
                $regexMatch: {
                    input: {$toLower: "$_id"},
                    regex: "^\\s*\\d+(\\s+\\d+)*\\s*$"
                }
            },
            equation_like: {
                $eq: [
                    {$substrCP: ["$_id", 0, 1]},
                    "="
                ]
            },
            insdc_missing_match: {
                $let: {
                    vars: {
                        lower: {$toLower: "$_id"}
                    },
                    in: {
                        $or: [
                            {$regexMatch: {input: "$$lower", regex: "control sample"}},
                            {$regexMatch: {input: "$$lower", regex: "data agreement established pre-2023"}},
                            {$regexMatch: {input: "$$lower", regex: "endangered species"}},
                            {$regexMatch: {input: "$$lower", regex: "human-identifiable"}},
                            {$regexMatch: {input: "$$lower", regex: "lab stock"}},
                            {$regexMatch: {input: "$$lower", regex: "missing"}},
                            {$regexMatch: {input: "$$lower", regex: "not applicable"}},
                            {$regexMatch: {input: "$$lower", regex: "not collected"}},
                            {$regexMatch: {input: "$$lower", regex: "not provided"}},
                            {$regexMatch: {input: "$$lower", regex: "restricted access"}},
                            {$regexMatch: {input: "$$lower", regex: "sample group"}},
                            {$regexMatch: {input: "$$lower", regex: "synthetic construct"}},
                            {$regexMatch: {input: "$$lower", regex: "third party data"}}
                        ]
                    }
                }
            }
        }
    },
    {
        $sort: {count: -1}
    },
    {
        $out: "biosamples_env_triad_value_counts_gt_1"
    }
])


