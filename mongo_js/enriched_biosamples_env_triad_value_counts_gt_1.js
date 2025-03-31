// NCBI
// < 4 minutes

// supersedes minimal_biosamples_env_triad_value_counts_gt_1.js
// follow with split_env_triad_values_from_perlmutter Makefile target (and more)
// < 3 minutes

const start = new Date();

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
            // Use $ifNull to ensure we always get a string
            length: {$strLenCP: {$ifNull: ["$_id", ""]}},
            envo_count: {
                $let: {
                    vars: {
                        lower: {$toLower: {$ifNull: ["$_id", ""]}},
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
                    input: {$toLower: {$ifNull: ["$_id", ""]}},
                    regex: "^\\s*\\d+(\\s+\\d+)*\\s*$"
                }
            },
            equation_like: {
                $eq: [
                    {$substrCP: [{$ifNull: ["$_id", ""]}, 0, 1]},
                    "="
                ]
            },
            insdc_missing_match: {
                $let: {
                    vars: {
                        lower: {$toLower: {$ifNull: ["$_id", ""]}}
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
            },
            other_missing_indicator: {
                $or: [
                    {$eq: ["$_id", null]},
                    {$eq: ["$_id", ""]},
                    {
                        $eq: [
                            {
                                $toLower: {
                                    $trim: {
                                        input: {$ifNull: ["$_id", ""]},
                                        chars: " "
                                    }
                                }
                            },
                            "na"
                        ]
                    },
                    {
                        $eq: [
                            {
                                $toLower: {
                                    $trim: {
                                        input: {$ifNull: ["$_id", ""]},
                                        chars: " "
                                    }
                                }
                            },
                            "n/a"
                        ]
                    },
                    {
                        $eq: [
                            {
                                $toLower: {
                                    $trim: {
                                        input: {$ifNull: ["$_id", ""]},
                                        chars: " "
                                    }
                                }
                            },
                            "null"
                        ]
                    }
                ]
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

// db.biosamples_env_triad_value_counts_gt_1.createIndex({env_triad_value: 1}, {unique: true});

const end = new Date();
print("Elapsed time: " + (end - start) + " ms");

// Elapsed time: 146285 ms
// 2.5 minutes