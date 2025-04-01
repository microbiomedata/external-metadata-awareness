const start = new Date();

db.biosamples_env_triad_value_counts_gt_1.createIndex({ env_triad_value: 1 })
db.biosamples_flattened.createIndex({ accession: 1 })

const end = new Date();
print("Elapsed time: " + (end - start) + " ms");


// const start = new Date();
//
// const end = new Date();
// print("Elapsed time: " + (end - start) + " ms");