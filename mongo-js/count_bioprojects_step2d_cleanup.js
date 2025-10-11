// Step 2d: Cleanup intermediate __tmp_hn_accessions collection
// Input: __tmp_hn_accessions → Output: (deleted)

const startTime = new Date();
print(`[${startTime.toISOString()}] Step 2d: Cleaning up intermediate collection`);

// Check if temp_bioproject_counts was created (Step 2c completed)
const outputCount = db.temp_bioproject_counts.estimatedDocumentCount();
if (outputCount === 0) {
    print(`[${new Date().toISOString()}] ⚠️  WARNING: temp_bioproject_counts is empty`);
    print(`[${new Date().toISOString()}] Step 2c may not have completed successfully`);
    print(`[${new Date().toISOString()}] Not dropping __tmp_hn_accessions (may need for debugging)`);
    quit(1);
}
print(`[${new Date().toISOString()}] temp_bioproject_counts has ${outputCount} records - Step 2c completed`);

// Check if temp collection exists
const tempCount = db.getCollection("__tmp_hn_accessions").estimatedDocumentCount();
if (tempCount === 0) {
    print(`[${new Date().toISOString()}] __tmp_hn_accessions already dropped or empty`);
    quit(0);
}
print(`[${new Date().toISOString()}] __tmp_hn_accessions has ${tempCount.toLocaleString()} records`);

// Drop intermediate collection
print(`[${new Date().toISOString()}] Dropping __tmp_hn_accessions...`);
db.getCollection("__tmp_hn_accessions").drop();

const endTime = new Date();
print(`[${endTime.toISOString()}] ✅ Step 2d complete`);
print(`[${endTime.toISOString()}] Intermediate collection cleaned up`);
