db.biosamples_measurements.aggregate([
  {
    $match: {
      parsed_quantity: { $exists: true, $type: "array", $ne: [] }
    }
  },
  {
    $unwind: "$parsed_quantity"
  },
  {
    $project: {
      unit_name: "$parsed_quantity.unit.name",
      count: 1
    }
  },
  {
    $group: {
      _id: "$unit_name",
      total_count: { $sum: "$count" }
    }
  },
  {
    $project: {
      _id: 0,
      unit_name: "$_id",
      total_count: 1
    }
  },
  {
    $sort: { total_count: -1 }
  },
  {
    $merge: {
      into: "measurements_inferred_units_totals",
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
])
