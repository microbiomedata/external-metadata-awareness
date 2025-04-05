db.biosamples_measurements.aggregate([
  // Unwind parsed_quantity array
  {
    $unwind: "$parsed_quantity"
  },
  // Project and compute the flattened fields
  {
    $project: {
      harmonized_name: 1,
      original_value: 1,
      count: 1,
      unit_entity: "$parsed_quantity.unit.entity",
      unit_name: "$parsed_quantity.unit.name",
      span_start: { $arrayElemAt: ["$parsed_quantity.span", 0] },
      span_end: { $arrayElemAt: ["$parsed_quantity.span", 1] },
      original_value_len: { $strLenCP: "$original_value" },
      original_value_coverage: {
        $subtract: [
          { $arrayElemAt: ["$parsed_quantity.span", 1] },
          { $arrayElemAt: ["$parsed_quantity.span", 0] }
        ]
      }
    }
  },
  // Write to flattened collection
  {
    $merge: {
      into: "biosamples_measurements_flattened",
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
])
