// Ensure biosample_accession index on sra_biosamples_bioprojects.
// Required by count_bioprojects_step2c_sra_join.js pre-flight check.
// Closes #402 — previously no make target created this index, so the
// composite count-biosamples-and-bioprojects-per-harmonized-name target
// would bail at step 2c after ~70 min of upstream work.

const startTime = new Date();
print(`[${startTime.toISOString()}] Ensuring biosample_accession index on sra_biosamples_bioprojects`);

const srcCount = db.sra_biosamples_bioprojects.estimatedDocumentCount();
if (srcCount === 0) {
    print(`[${new Date().toISOString()}] ❌ ERROR: sra_biosamples_bioprojects is empty`);
    print(`[${new Date().toISOString()}] Load SRA pairs first (see sra_metadata.Makefile)`);
    quit(1);
}
print(`[${new Date().toISOString()}] sra_biosamples_bioprojects has ${srcCount.toLocaleString()} records`);

const existing = db.sra_biosamples_bioprojects.getIndexes()
    .find(idx => idx.key.biosample_accession === 1);
if (existing) {
    print(`[${new Date().toISOString()}] ✓ Index already exists: ${existing.name}`);
    quit(0);
}

print(`[${new Date().toISOString()}] Creating idx_biosample_accession (a few minutes on 35M+ rows)...`);
db.sra_biosamples_bioprojects.createIndex(
    {biosample_accession: 1},
    {name: "idx_biosample_accession"}
);

const endTime = new Date();
const elapsed = ((endTime - startTime) / 1000).toFixed(2);
print(`[${endTime.toISOString()}] ✅ Index created in ${elapsed}s`);
