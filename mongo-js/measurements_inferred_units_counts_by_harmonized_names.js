db.biosamples_measurements.aggregate([
    // Only keep docs where parsed_quantity is a non-empty array
    {
        $match: {
            parsed_quantity: {$exists: true, $type: "array", $ne: []}
        }
    },
    // Break apart parsed_quantity into individual entries
    {
        $unwind: "$parsed_quantity"
    },
    // Extract relevant fields
    {
        $project: {
            harmonized_name: 1,
            unit_name: "$parsed_quantity.unit.name",
            count: 1
        }
    },
    // Group by harmonized_name and unit name
    {
        $group: {
            _id: {
                harmonized_name: "$harmonized_name",
                unit_name: "$unit_name"
            },
            total_count: {$sum: "$count"}
        }
    },
    // Format output nicely
    {
        $project: {
            _id: 0,
            harmonized_name: "$_id.harmonized_name",
            unit_name: "$_id.unit_name",
            total_count: 1
        }
    },
    // Write to target collection
    {
        $merge: {
            into: "measurements_inferred_units_counts_by_harmonized_names",
            whenMatched: "replace",
            whenNotMatched: "insert"
        }
    }
])
