// Step 2a: Deduplicate harmonized_name + accession pairs from biosamples_attributes
// Creates intermediate collection to make SRA lookup faster
// Input: biosamples_attributes → Output: __tmp_hn_accessions

const startTime = new Date();
print(`[${startTime.toISOString()}] Step 2a: Deduplicating harmonized_name + accession pairs`);

// Check if already done
const existingCount = db.getCollection("__tmp_hn_accessions").estimatedDocumentCount();
if (existingCount > 0) {
    print(`[${new Date().toISOString()}] ✓ Step 2a already complete (__tmp_hn_accessions has ${existingCount.toLocaleString()} records)`);
    print(`[${new Date().toISOString()}] Skipping - drop __tmp_hn_accessions to rerun`);
    quit(0);
}

// Drop output collection
db.getCollection("__tmp_hn_accessions").drop();

print(`[${new Date().toISOString()}] Running aggregation (may take 60-90 min for 712M records)...`);
db.biosamples_attributes.aggregate([
    {
        $match: {
            harmonized_name: {$exists: true, $ne: "", $ne: null},
            accession: {$exists: true, $ne: "", $ne: null}
        }
    },
    // Deduplicate harmonized_name + accession pairs
    {
        $group: {
            _id: {h: "$harmonized_name", a: "$accession"}
        }
    },
    {
        $project: {
            harmonized_name: "$_id.h",
            accession: "$_id.a",
            _id: 0
        }
    },
    {
        $out: "__tmp_hn_accessions"
    }
], {allowDiskUse: true});

const endTime = new Date();
const elapsed = ((endTime - startTime) / 1000).toFixed(2);
const resultCount = db.getCollection("__tmp_hn_accessions").countDocuments();

print(`[${endTime.toISOString()}] ✅ Step 2a complete`);
print(`[${endTime.toISOString()}] Created ${resultCount.toLocaleString()} unique harmonized_name+accession pairs`);
print(`[${endTime.toISOString()}] Elapsed: ${elapsed} seconds (${(elapsed/60).toFixed(1)} minutes)`);
print(`[${endTime.toISOString()}] Reduced 712M records → ${resultCount.toLocaleString()} unique pairs`);
