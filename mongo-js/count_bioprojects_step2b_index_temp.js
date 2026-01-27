// Step 2b: Create index on __tmp_hn_accessions for fast SRA lookup
// Input: __tmp_hn_accessions → Output: indexed __tmp_hn_accessions

const startTime = new Date();
print(`[${startTime.toISOString()}] Step 2b: Creating index on __tmp_hn_accessions.accession`);

// Check prerequisite
const tempCount = db.getCollection("__tmp_hn_accessions").estimatedDocumentCount();
if (tempCount === 0) {
    print(`[${new Date().toISOString()}] ❌ ERROR: __tmp_hn_accessions is empty`);
    print(`[${new Date().toISOString()}] Run Step 2a first`);
    quit(1);
}
print(`[${new Date().toISOString()}] __tmp_hn_accessions has ${tempCount.toLocaleString()} records`);

// Create index (critical for fast lookup)
print(`[${new Date().toISOString()}] Creating index (may take 5-10 min)...`);
db.getCollection("__tmp_hn_accessions").createIndex({accession: 1}, {background: true});

const endTime = new Date();
const elapsed = ((endTime - startTime) / 1000).toFixed(2);

print(`[${endTime.toISOString()}] ✅ Step 2b complete`);
print(`[${endTime.toISOString()}] Index created in ${elapsed} seconds`);

// Verify index exists
const indexes = db.getCollection("__tmp_hn_accessions").getIndexes();
const hasIndex = indexes.some(idx => idx.key.accession);
print(`[${endTime.toISOString()}] Verification: accession index ${hasIndex ? '✅ EXISTS' : '❌ MISSING'}`);
