// NMDC Submissions

db.submission_biosample_rows.aggregate([
  { $unwind: "$row_data" },
  { $group: {
      _id: "$row_data.field",
      count: { $sum: 1 }
  }},
  { $project: {
      _id: 0,
      field: "$_id",
      count: 1
  }},
  { $out: "submission_biosample_slot_counts" }
])
