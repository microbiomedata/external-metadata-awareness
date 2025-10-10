// Step 1: Dedupe harmonized_name + accession → count biosamples per harmonized_name
// Input: biosamples_attributes → Output: __tmp_hn_counts
// Part of atomic biosample counting workflow (Issue #237)

const startTime = new Date();
print(`[${startTime.toISOString()}] Step 1: Counting biosamples per harmonized_name (dedupe)`);

// Check if already done (use getCollection for names with __)
const existingCount = db.getCollection("__tmp_hn_counts").estimatedDocumentCount();
if (existingCount > 0) {
    print(`[${new Date().toISOString()}] ✓ Step 1 already complete (__tmp_hn_counts has ${existingCount} records)`);
    print(`[${new Date().toISOString()}] Skipping - delete __tmp_hn_counts to rerun`);
    quit(0);
}

// Drop output collection
db.getCollection("__tmp_hn_counts").drop();

// Deduplicate harmonized_name + accession pairs and count
print(`[${new Date().toISOString()}] Running aggregation (may take 30-60 min for 712M records)...`);
db.biosamples_attributes.aggregate([
    {
        $match: {
            harmonized_name: { $type: "string", $ne: "" },
            accession: { $type: "string", $ne: "" }
        }
    },
    {
        $group: {
            _id: { h: "$harmonized_name", a: "$accession" }
        }
    },
    {
        $group: {
            _id: "$_id.h",
            biosample_count: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            harmonized_name: "$_id",
            biosample_count: 1
        }
    },
    {
        $out: "__tmp_hn_counts"
    }
], { allowDiskUse: true });

const endTime = new Date();
const elapsed = ((endTime - startTime) / 1000).toFixed(2);
const resultCount = db.getCollection("__tmp_hn_counts").countDocuments();

print(`[${endTime.toISOString()}] ✅ Step 1 complete`);
print(`[${endTime.toISOString()}] Created ${resultCount} records in __tmp_hn_counts`);
print(`[${endTime.toISOString()}] Elapsed: ${elapsed} seconds`);
