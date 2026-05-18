// One-shot backfill: add model_content to existing biosamples_flattened
// without rewriting unrelated fields.
//
// Input:  ncbi_metadata.biosamples (Models.Model.content present on ~100% of docs)
// Output: ncbi_metadata.biosamples_flattened gains model_content field in place
//
// Use only when biosamples_flattened was built before flatten_biosamples.js
// gained the model_content projection. Subsequent full rebuilds of
// biosamples_flattened include the field natively; this script is not
// required as part of the standing pipeline.
//
// $merge with `on: accession` requires a unique index on the target's
// accession field. The existing {accession: 1} index is non-unique, so we
// rebuild it as unique. Accession uniqueness in biosamples_flattened was
// verified on M5 (56254160 docs, zero duplicate groups).

const target = db.biosamples_flattened;

const idx = target.getIndexes().find(i =>
    JSON.stringify(i.key) === JSON.stringify({accession: 1})
);
if (!idx || !idx.unique) {
    if (idx) {
        print("Dropping non-unique {accession: 1} index...");
        target.dropIndex(idx.name);
    }
    print("Creating unique {accession: 1} index...");
    target.createIndex({accession: 1}, {unique: true});
}

print("Merging Models.Model.content into biosamples_flattened.model_content...");
db.biosamples.aggregate([
    {
        $project: {
            _id: 0,
            accession: 1,
            model_content: {$ifNull: ["$Models.Model.content", null]}
        }
    },
    {
        $merge: {
            into: "biosamples_flattened",
            on: "accession",
            whenMatched: "merge",
            whenNotMatched: "discard"
        }
    }
]);
print("Done.");
