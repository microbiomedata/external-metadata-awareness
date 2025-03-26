db.biosamples.aggregate([
    {$unwind: "$Attributes.Attribute"},
    {$match: {"Attributes.Attribute.harmonized_name": {$exists: true, $ne: null}}},
    {
        $group: {
            _id: {
                attribute_name: "$Attributes.Attribute.attribute_name",
                harmonized_name: "$Attributes.Attribute.harmonized_name"
            },
            count: {$sum: 1}
        }
    },
    {$match: {count: {$gte: 2}}},
    {
        $project: {
            _id: 0,
            attribute_name: "$_id.attribute_name",
            harmonized_name: "$_id.harmonized_name",
            count: 1,
            likely_sra_key_name: {
                $function: {
                    body: function (name) {
                        return name
                                .replace(/[^\w]/g, "_")  // replace all non-word characters
                                .toLowerCase()           // convert to lowercase
                            + "_sam";                // add suffix
                    },
                    args: ["$_id.attribute_name"],
                    lang: "js"
                }
            }
        }
    },
    {$sort: {count: -1}},
    {$out: "biosample_attribute_name_counts_flat_gt_1"}
])
