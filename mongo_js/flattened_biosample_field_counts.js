db.flattened_biosample.aggregate([
  {
    $project: {
      kvArray: { $objectToArray: "$$ROOT" }
    }
  },
  { $unwind: "$kvArray" },
  { $match: { "kvArray.v": { $ne: null } } },
  {
    $group: {
      _id: "$kvArray.k",
      count: { $sum: 1 }
    }
  },
  {
    $out: "flattened_biosample_field_counts"
  }
])
