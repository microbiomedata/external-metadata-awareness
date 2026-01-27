// Step 1: Count unique biosamples per harmonized_name (for harmonized_name_usage_stats)
// Avoids $addToSet memory limit by deduping first
// Input: biosamples_attributes → Output: temp_biosample_counts

const startTime = new Date();
print(`[${startTime.toISOString()}] Step 1: Counting unique biosamples per harmonized_name`);

// Check if already done
const existingCount = db.temp_biosample_counts.estimatedDocumentCount();
if (existingCount > 0) {
    print(`[${new Date().toISOString()}] ✓ Step 1 already complete (temp_biosample_counts has ${existingCount} records)`);
    print(`[${new Date().toISOString()}] Skipping - drop temp_biosample_counts to rerun`);
    quit(0);
}

// Drop output collection
db.temp_biosample_counts.drop();

// Dedupe harmonized_name + accession pairs, then count
print(`[${new Date().toISOString()}] Running aggregation (may take 30-60 min for 712M records)...`);
db.biosamples_attributes.aggregate([
    {
        $match: {
            harmonized_name: {$exists: true, $ne: "", $ne: null},
            accession: {$exists: true, $ne: "", $ne: null}
        }
    },
    // First $group: deduplicate harmonized_name + accession pairs
    // This prevents building huge arrays in memory
    {
        $group: {
            _id: {h: "$harmonized_name", a: "$accession"}
        }
    },
    // Second $group: count unique accessions per harmonized_name
    {
        $group: {
            _id: "$_id.h",
            unique_biosamples_count: {$sum: 1}
        }
    },
    {
        $project: {
            harmonized_name: "$_id",
            unique_biosamples_count: 1,
            _id: 0
        }
    },
    {
        $out: "temp_biosample_counts"
    }
], {allowDiskUse: true});

const endTime = new Date();
const elapsed = ((endTime - startTime) / 1000).toFixed(2);
const resultCount = db.temp_biosample_counts.countDocuments();

print(`[${endTime.toISOString()}] ✅ Step 1 complete`);
print(`[${endTime.toISOString()}] Created ${resultCount} biosample count records`);
print(`[${endTime.toISOString()}] Elapsed: ${elapsed} seconds`);
