const start = new Date();

db.env_triads.createIndex({"env_broad_scale.components.curie_lc": 1})
db.env_triads.createIndex({"env_local_scale.components.curie_lc": 1})
db.env_triads.createIndex({"env_medium.components.curie_lc": 1})

db.env_triad_component_in_scope_curies_lc.createIndex({curie_lc: 1})


const end = new Date();
print("Elapsed time: " + (end - start) + " ms");
