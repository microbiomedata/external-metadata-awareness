// Materialize ncbi_metadata.sra_biosamples_bioprojects from sra_metadata.sra_metadata
// via a single cross-DB aggregation.
//
// Input:  sra_metadata.sra_metadata (full SRA parquet load, one row per run)
// Output: ncbi_metadata.sra_biosamples_bioprojects (deduplicated 2-column pair table)
//
// Field-name shim: source has biosample / bioproject; destination has
// biosample_accession / bioproject_accession (the names existing downstream consumers
// expect). $project performs the rename at write time.
//
// Cross-DB write: $out: {db, coll} is native in Mongo 4.4+.
// Dedup: $group collapses run-level multiplicity to (biosample, bioproject) pairs.
//
// Expects the source-side index {biosample: 1, bioproject: 1} on sra_metadata.sra_metadata
// (built ad-hoc; see issue #392 for proposed make target). Without it, the $group is a
// full collection scan. With it, the aggregation runs in tens of minutes on ~42M rows.

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting cross-DB derivation of sra_biosamples_bioprojects from sra_metadata.sra_metadata`);

const srcDb = db.getSiblingDB("sra_metadata");
const srcColl = srcDb.sra_metadata;

const srcCount = srcColl.estimatedDocumentCount();
print(`[${new Date().toISOString()}] Source: sra_metadata.sra_metadata (${srcCount.toLocaleString()} rows)`);

if (srcCount === 0) {
    print(`[${new Date().toISOString()}] ERROR: source collection is empty. Run the SRA parquet loader first.`);
    quit(1);
}

print(`[${new Date().toISOString()}] Running aggregation (expect ~10-30 min on 42M rows with the {biosample, bioproject} index in place)...`);

srcColl.aggregate([
    {
        // Filter null and empty-string in one operator — JS object literals
        // silently keep only the last duplicate key, so {$ne: null, $ne: ""}
        // collapses to {$ne: ""} and lets null values through.
        $match: {
            biosample:  {$exists: true, $nin: [null, ""]},
            bioproject: {$exists: true, $nin: [null, ""]}
        }
    },
    {
        $group: {
            _id: {b: "$biosample", p: "$bioproject"}
        }
    },
    {
        $project: {
            _id: 0,
            biosample_accession:  "$_id.b",
            bioproject_accession: "$_id.p"
        }
    },
    {
        $out: {db: "ncbi_metadata", coll: "sra_biosamples_bioprojects"}
    }
], {allowDiskUse: true});

const destDb = db.getSiblingDB("ncbi_metadata");
const destCount = destDb.sra_biosamples_bioprojects.countDocuments();
print(`[${new Date().toISOString()}] Wrote ${destCount.toLocaleString()} unique (biosample, bioproject) pairs to ncbi_metadata.sra_biosamples_bioprojects`);

const elapsed = (new Date() - startTime) / 1000;
print(`[${new Date().toISOString()}] Done in ${elapsed.toFixed(1)}s. Run \`index-sra-pairs\` (after #381 fix) to build downstream indexes.`);
