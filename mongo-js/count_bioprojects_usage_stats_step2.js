// Step 2: Count unique bioprojects per harmonized_name (for harmonized_name_usage_stats)
// Avoids $addToSet memory limit by deduping first
// Input: biosamples_attributes + sra_biosamples_bioprojects → Output: temp_bioproject_counts

const startTime = new Date();
print(`[${startTime.toISOString()}] Step 2: Counting unique bioprojects per harmonized_name via SRA linkage`);

// Check prerequisite
const sraCount = db.sra_biosamples_bioprojects.estimatedDocumentCount();
if (sraCount === 0) {
    print(`[${new Date().toISOString()}] ❌ ERROR: sra_biosamples_bioprojects collection is empty`);
    print(`[${new Date().toISOString()}] Cannot count bioprojects without SRA linkage data`);
    quit(1);
}
print(`[${new Date().toISOString()}] SRA linkage collection has ${sraCount.toLocaleString()} records`);

// Drop output collection
db.temp_bioproject_counts.drop();

// Dedupe harmonized_name + accession pairs, lookup bioprojects, dedupe again, then count
print(`[${new Date().toISOString()}] Running aggregation (may take 40-80 min - includes SRA lookup join)...`);
db.biosamples_attributes.aggregate([
    {
        $match: {
            harmonized_name: {$exists: true, $ne: "", $ne: null},
            accession: {$exists: true, $ne: "", $ne: null}
        }
    },
    // First $group: deduplicate harmonized_name + accession pairs
    {
        $group: {
            _id: {h: "$harmonized_name", a: "$accession"}
        }
    },
    // Lookup bioprojects via SRA linkage
    {
        $lookup: {
            from: "sra_biosamples_bioprojects",
            localField: "_id.a",
            foreignField: "biosample_accession",
            as: "bp"
        }
    },
    // Unwind bioproject results (may be multiple bioprojects per biosample)
    {
        $unwind: {path: "$bp", preserveNullAndEmptyArrays: false}
    },
    // Second $group: deduplicate harmonized_name + bioproject pairs
    {
        $group: {
            _id: {h: "$_id.h", bp: "$bp.bioproject_accession"}
        }
    },
    // Third $group: count unique bioprojects per harmonized_name
    {
        $group: {
            _id: "$_id.h",
            unique_bioprojects_count: {$sum: 1}
        }
    },
    {
        $project: {
            harmonized_name: "$_id",
            unique_bioprojects_count: 1,
            _id: 0
        }
    },
    {
        $out: "temp_bioproject_counts"
    }
], {allowDiskUse: true});

const endTime = new Date();
const elapsed = ((endTime - startTime) / 1000).toFixed(2);
const resultCount = db.temp_bioproject_counts.countDocuments();

print(`[${endTime.toISOString()}] ✅ Step 2 complete`);
print(`[${endTime.toISOString()}] Created ${resultCount} bioproject count records`);
print(`[${endTime.toISOString()}] Elapsed: ${elapsed} seconds`);
