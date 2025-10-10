// Count biosamples per harmonized_name from biosamples_attributes
// Fixed version - db references moved inside execution
// Input: biosamples_attributes → Output: harmonized_name_biosample_counts

// Logging helper
function ts(msg){ print("[" + new Date().toISOString() + "] " + msg) }

ts("Starting biosample counts per harmonized_name…");

// Step 1: Create required indexes for performance
ts("Creating/ensuring indexes…");
try {
  db.biosamples_attributes.createIndex({ harmonized_name: 1, accession: 1 });
} catch(e) {
  print("Index exists: " + e.message);
}
try {
  db.biosamples_attributes.createIndex({ accession: 1 });
} catch(e) {
  print("Index exists: " + e.message);
}

// Step 2: Quick baseline statistics
const totalAttributes = db.biosamples_attributes.estimatedDocumentCount();
const totalUniqueAccessions = db.biosamples_attributes.aggregate([
  { $match: { accession: { $type: "string", $ne: "" } } },
  { $group: { _id: "$accession" } },
  { $count: "total" }
], { allowDiskUse: true }).toArray()[0]?.total ?? 0;

ts(`Total attribute records: ${totalAttributes.toLocaleString()}`);
ts(`Total unique biosamples (accessions): ${totalUniqueAccessions.toLocaleString()}`);

// Step 3: Build temporary table #1: biosample_count per harmonized_name
ts("Computing biosample_count per harmonized_name (dedupe by accession) …");
db.__tmp_hn_counts.drop();
db.biosamples_attributes.aggregate([
  { $match: {
      harmonized_name: { $type: "string", $ne: "" },
      accession: { $type: "string", $ne: "" }
    } },
  { $group: { _id: { h: "$harmonized_name", a: "$accession" } } },
  { $group: { _id: "$_id.h", biosample_count: { $sum: 1 } } },
  { $project: { _id: 0, harmonized_name: "$_id", biosample_count: 1 } },
  { $out: "__tmp_hn_counts" }
], { allowDiskUse: true });

ts(`Created ${db.__tmp_hn_counts.countDocuments()} harmonized_name records in temp collection`);

// Step 4: Build temporary table #2: totals and unit coverage per harmonized_name
ts("Computing total_attribute_records and has_unit_records per harmonized_name …");
db.__tmp_hn_totals.drop();
db.biosamples_attributes.aggregate([
  { $match: { harmonized_name: { $type: "string", $ne: "" } } },
  { $group: {
      _id: "$harmonized_name",
      total_attribute_records: { $sum: 1 },
      has_unit_records: {
        $sum: {
          $cond: [
            { $and: [
                { $ne: ["$unit", null] },
                { $ne: ["$unit", ""] }
              ]},
            1, 0
          ]
        }
      }
    } },
  { $project: { _id: 0,
      harmonized_name: "$_id",
      total_attribute_records: 1,
      has_unit_records: 1,
      unit_coverage_percent: {
        $cond: [
          { $gt: ["$total_attribute_records", 0] },
          { $round: [{ $multiply: [ { $divide: ["$has_unit_records", "$total_attribute_records"] }, 100 ] }, 2] },
          0
        ]
      }
    } },
  { $out: "__tmp_hn_totals" }
], { allowDiskUse: true });

ts(`Created ${db.__tmp_hn_totals.countDocuments()} records in totals temp collection`);

// Step 5: Join temp tables → final output
ts("Joining temp tables and writing final collection …");
db.harmonized_name_biosample_counts.drop();
db.__tmp_hn_counts.aggregate([
  { $lookup: {
      from: "__tmp_hn_totals",
      localField: "harmonized_name",
      foreignField: "harmonized_name",
      as: "t"
    } },
  { $unwind: { path: "$t", preserveNullAndEmptyArrays: true } },
  { $addFields: {
      total_attribute_records: "$t.total_attribute_records",
      has_unit_records: "$t.has_unit_records",
      unit_coverage_percent: "$t.unit_coverage_percent",
      coverage_percent: {
        $cond: [
          { $gt: [ totalUniqueAccessions, 0 ] },
          { $round: [{ $multiply: [ { $divide: ["$biosample_count", totalUniqueAccessions] }, 100 ] }, 2] },
          0
        ]
      }
    } },
  { $project: { t: 0 } },
  { $sort: { biosample_count: -1 } },
  { $out: "harmonized_name_biosample_counts" }
], { allowDiskUse: true });

// Step 6: Create indexes on the output collection
ts("Creating indexes on output collection …");
db.harmonized_name_biosample_counts.createIndex({ harmonized_name: 1 }, { name: "hn_1" });
db.harmonized_name_biosample_counts.createIndex({ biosample_count: -1 }, { name: "biosample_count_-1" });
db.harmonized_name_biosample_counts.createIndex({ unit_coverage_percent: -1 }, { name: "unit_cov_-1" });

// Step 7: Generate summary statistics
const resultsCount = db.harmonized_name_biosample_counts.estimatedDocumentCount();
const totalCoveredBiosamples = db.harmonized_name_biosample_counts.aggregate([
  { $group: { _id: null, total: { $sum: "$biosample_count" } } }
]).toArray()[0]?.total ?? 0;
const fieldsWithUnits = db.harmonized_name_biosample_counts.countDocuments({ has_unit_records: { $gt: 0 } });

ts("✅ Biosample counting complete");
ts(`Unique harmonized_names: ${resultsCount.toLocaleString()}`);
ts(`Total biosample-field combinations: ${totalCoveredBiosamples.toLocaleString()}`);
ts(`Fields with some unit assertions: ${fieldsWithUnits} of ${resultsCount} (${(fieldsWithUnits/resultsCount*100).toFixed(1)}%)`);
ts(`Average fields per biosample: ${(totalCoveredBiosamples / Math.max(totalUniqueAccessions,1)).toFixed(1)}`);

// Step 8: Cleanup temporary collections
ts("Cleaning up temporary collections…");
db.__tmp_hn_counts.drop();
db.__tmp_hn_totals.drop();

ts("Done!");
