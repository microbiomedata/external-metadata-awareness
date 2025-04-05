db.biosamples_measurements.aggregate([
  // Step 1: Normalize parsed_quantity as a safe array (or [])
  {
    $project: {
      harmonized_name: 1,
      count: 1,
      parsed_quantity_safe: {
        $cond: [
          {
            $and: [
              { $isArray: "$parsed_quantity" },
              { $gt: [{ $size: "$parsed_quantity" }, 0] }
            ]
          },
          "$parsed_quantity",
          []
        ]
      }
    }
  },
  // Step 2: Compute flags for types of measurement evidence
  {
    $project: {
      harmonized_name: 1,
      count: 1,
      has_parsed_quantity: {
        $gt: [{ $size: "$parsed_quantity_safe" }, 0]
      },
      has_dimensional: {
        $gt: [
          {
            $size: {
              $filter: {
                input: "$parsed_quantity_safe",
                as: "pq",
                cond: { $ne: ["$$pq.unit.name", "dimensionless"] }
              }
            }
          },
          0
        ]
      },
      has_range_like: {
        $gt: [
          {
            $size: {
              $filter: {
                input: "$parsed_quantity_safe",
                as: "pq",
                cond: { $ne: ["$$pq.uncertainty", null] }
              }
            }
          },
          0
        ]
      },
      has_range_like_with_units: {
        $gt: [
          {
            $size: {
              $filter: {
                input: "$parsed_quantity_safe",
                as: "pq",
                cond: {
                  $and: [
                    { $ne: ["$$pq.uncertainty", null] },
                    { $ne: ["$$pq.unit.name", "dimensionless"] }
                  ]
                }
              }
            }
          },
          0
        ]
      }
    }
  },
  // Step 3: Group by harmonized_name
  {
    $group: {
      _id: "$harmonized_name",
      total_count: { $sum: "$count" },
      parsed_quantity_count: {
        $sum: {
          $cond: ["$has_parsed_quantity", "$count", 0]
        }
      },
      dimensional_count: {
        $sum: {
          $cond: ["$has_dimensional", "$count", 0]
        }
      },
      range_like_count: {
        $sum: {
          $cond: ["$has_range_like", "$count", 0]
        }
      },
      range_like_with_units_count: {
        $sum: {
          $cond: ["$has_range_like_with_units", "$count", 0]
        }
      }
    }
  },
  // Step 4: Compute proportions
  {
    $project: {
      harmonized_name: "$_id",
      _id: 0,
      total_count: 1,
      parsed_quantity_count: 1,
      parsed_quantity_proportion: {
        $cond: [
          { $eq: ["$total_count", 0] },
          0,
          { $divide: ["$parsed_quantity_count", "$total_count"] }
        ]
      },
      dimensional_count: 1,
      dimensional_proportion: {
        $cond: [
          { $eq: ["$total_count", 0] },
          0,
          { $divide: ["$dimensional_count", "$total_count"] }
        ]
      },
      range_like_count: 1,
      range_like_proportion: {
        $cond: [
          { $eq: ["$total_count", 0] },
          0,
          { $divide: ["$range_like_count", "$total_count"] }
        ]
      },
      range_like_with_units_count: 1,
      range_like_with_units_proportion: {
        $cond: [
          { $eq: ["$total_count", 0] },
          0,
          { $divide: ["$range_like_with_units_count", "$total_count"] }
        ]
      }
    }
  },
  // Step 5: Write results to new collection
  {
    $merge: {
      into: "measurement_evidence_by_harmonized_name",
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
])
