// Create indexes on sra_biosamples_bioprojects.
// Prerequisite for count_bioprojects_step2c_sra_join.js (pre-flights for
// biosample_accession index) and any cross-source join against the pair table.
// Idempotent: if an index with the same key already exists under any name,
// it is skipped (a different-name existing index is treated as success).

const startTime = new Date();
print(`[${startTime.toISOString()}] Creating indexes on sra_biosamples_bioprojects`);

const coll = db.sra_biosamples_bioprojects;

const specs = [
    {key: {biosample_accession: 1}, options: {name: 'idx_biosample'}},
    {key: {bioproject_accession: 1}, options: {name: 'idx_bioproject'}},
    {key: {biosample_accession: 1, bioproject_accession: 1}, options: {name: 'idx_compound'}}
];

function keyEquals(a, b) {
    const ak = Object.keys(a);
    const bk = Object.keys(b);
    if (ak.length !== bk.length) return false;
    for (const k of ak) {
        if (a[k] !== b[k]) return false;
    }
    return true;
}

const existing = coll.getIndexes();

specs.forEach(spec => {
    const sameKey = existing.find(i => keyEquals(i.key, spec.key));
    if (sameKey) {
        print(`[${new Date().toISOString()}] ✓ ${spec.options.name} skipped — same key already indexed as "${sameKey.name}"`);
        return;
    }
    const t0 = new Date();
    coll.createIndex(spec.key, spec.options);
    const elapsed = ((new Date() - t0) / 1000).toFixed(2);
    print(`[${new Date().toISOString()}] ✓ ${spec.options.name} created (${elapsed}s)`);
});

print(`[${new Date().toISOString()}] Done. ${coll.getIndexes().length} indexes on sra_biosamples_bioprojects.`);
