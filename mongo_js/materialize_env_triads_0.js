const start = new Date();

const
    cursor = db.biosamples_env_triad_value_counts_gt_1.find({}, {components: 1});

let bulk = db.biosamples_env_triad_value_counts_gt_1.initializeUnorderedBulkOp();
let counter = 0;

cursor.forEach(doc => {
    const updatedComponents = (doc.components || []).map(c => {
        if (!c.prefix || !c.local) return c; // skip if data is missing
        return {
            ...c,
            curie_lc: `${c.prefix}:${c.local}`.toLowerCase()
        };
    });

    bulk.find({_id: doc._id}).updateOne({$set: {components: updatedComponents}});
    counter++;

    if (counter % 1000 === 0) {
        bulk.execute();
        bulk = db.biosamples_env_triad_value_counts_gt_1.initializeUnorderedBulkOp();
    }
});

if (counter % 1000 !== 0) {
    bulk.execute();
}

print(`Updated ${counter} documents.`);

const end = new Date();
print("Elapsed time: " + (end - start) + " ms");
