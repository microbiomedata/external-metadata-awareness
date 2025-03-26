db.biosamples.aggregate([
    {
        $project: {
            accession: 1,
            ids_array: {
                $cond: {
                    if: {$isArray: "$Ids.Id"},
                    then: "$Ids.Id",
                    else: {
                        $cond: {
                            if: {$gt: ["$Ids.Id", null]},
                            then: ["$Ids.Id"],
                            else: []
                        }
                    }
                }
            }
        }
    },
    {$unwind: "$ids_array"},
    {
        $project: {
            _id: false,  // This line prevents duplicate key errors
            accession: 1,
            content: "$ids_array.content",
            db: "$ids_array.db",
            label: "$ids_array.db_label",
            is_primary: "$ids_array.is_primary",
            is_hidden: "$ids_array.is_hidden"
        }
    },
    {
        $out: "biosamples_ids"
    }
])


