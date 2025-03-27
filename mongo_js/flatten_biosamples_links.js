// NCBI

db.biosamples.aggregate([
    {
        $project: {
            accession: 1,
            links_array: {
                $cond: {
                    if: {$isArray: "$Links.Link"},
                    then: "$Links.Link",
                    else: {
                        $cond: {
                            if: {$gt: ["$Links.Link", null]},
                            then: ["$Links.Link"],
                            else: []
                        }
                    }
                }
            }
        }
    },
    {$unwind: "$links_array"},
    {
        $project: {
            _id: false,  // Prevents duplicate key error
            accession: 1,
            content: "$links_array.content",
            type: "$links_array.type",
            label: "$links_array.label",
            target: "$links_array.target",
            submission_id: "$links_array.submission_id"
        }
    },
    {
        $out: "biosamples_links"
    }
])


