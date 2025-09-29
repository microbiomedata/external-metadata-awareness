// Count biosamples per harmonized_name from biosamples_attributes
// Input: biosamples_attributes → Output: harmonized_name_biosample_counts
// Optimized version avoiding $addToSet memory explosion

// Logging helper
function ts(msg){ print("[" + new Date().toISOString() + "] " + msg) }

ts("Starting biosample counts per harmonized_name…");
const SRC = db.biosamples_attributes;
const OUT = db.harmonized_name_biosample_counts;
const TMP_COUNTS = db.__tmp_hn_counts;
const TMP_TOTALS = db.__tmp_hn_totals;

// Step 1: Create required indexes for performance
ts("Creating/ensuring indexes…");
SRC.createIndex({ harmonized_name: 1, accession: 1 });
SRC.createIndex({ accession: 1 });

// Step 2: Quick baseline statistics  
const totalAttributes = SRC.estimatedDocumentCount();
const totalUniqueAccessions = SRC.aggregate([
  { $match: { accession: { $type: "string", $ne: "" } } },
  { $group: { _id: "$accession" } },
  { $count: "total" }
], { allowDiskUse: true }).toArray()[0]?.total ?? 0;

ts(`Total attribute records: ${totalAttributes.toLocaleString()}`);
ts(`Total unique biosamples (accessions): ${totalUniqueAccessions.toLocaleString()}`);

// Step 3: Build temporary table #1: biosample_count per harmonized_name
// (distinct (harmonized_name, accession) → count per harmonized_name)
ts("Computing biosample_count per harmonized_name (dedupe by accession) …");
TMP_COUNTS.drop();
SRC.aggregate([
  { $match: {
      harmonized_name: { $type: "string", $ne: "" },
      accession: { $type: "string", $ne: "" }
    } },
  { $group: { _id: { h: "$harmonized_name", a: "$accession" } } },
  { $group: { _id: "$_id.h", biosample_count: { $sum: 1 } } },
  { $project: { _id: 0, harmonized_name: "$_id", biosample_count: 1 } },
  { $merge: { into: TMP_COUNTS.getName(), whenMatched: "replace", whenNotMatched: "insert" } }
], { allowDiskUse: true });

// Step 4: Build temporary table #2: totals and unit coverage per harmonized_name
ts("Computing total_attribute_records and has_unit_records per harmonized_name …");
TMP_TOTALS.drop();
SRC.aggregate([
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
  { $merge: { into: TMP_TOTALS.getName(), whenMatched: "replace", whenNotMatched: "insert" } }
], { allowDiskUse: true });

// Step 5: Join temp tables → final output, add coverage_percent using the JS scalar
ts("Joining temp tables and writing final collection …");
OUT.drop();
TMP_COUNTS.aggregate([
  { $lookup: {
      from: TMP_TOTALS.getName(),
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
  { $merge: { into: OUT.getName(), whenMatched: "replace", whenNotMatched: "insert" } }
], { allowDiskUse: true });

// Step 6: Create indexes on the output collection
ts("Creating indexes on output collection …");
OUT.createIndex({ harmonized_name: 1 }, { name: "hn_1" });
OUT.createIndex({ biosample_count: -1 }, { name: "biosample_count_-1" });
OUT.createIndex({ unit_coverage_percent: -1 }, { name: "unit_cov_-1" });

// Step 7: Generate summary statistics
const resultsCount = OUT.estimatedDocumentCount();
const totalCoveredBiosamples = OUT.aggregate([
  { $group: { _id: null, total: { $sum: "$biosample_count" } } }
]).toArray()[0]?.total ?? 0;
const fieldsWithUnits = OUT.countDocuments({ has_unit_records: { $gt: 0 } });

ts("✅ Biosample counting complete");
ts(`Unique harmonized_names: ${resultsCount.toLocaleString()}`);
ts(`Total biosample-field combinations: ${totalCoveredBiosamples.toLocaleString()}`);
ts(`Fields with some unit assertions: ${fieldsWithUnits} of ${resultsCount} (${(fieldsWithUnits/resultsCount*100).toFixed(1)}%)`);
ts(`Average fields per biosample: ${(totalCoveredBiosamples / Math.max(totalUniqueAccessions,1)).toFixed(1)}`);
ts(`Collection created: ${OUT.getName()}`);

// Step 8: Cleanup temporary collections
ts("Cleaning up temporary collections…");
TMP_COUNTS.drop();
TMP_TOTALS.drop();