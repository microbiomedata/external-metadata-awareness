
const start = new Date();

// Optimize the updateMany lookup phase
db.env_triads.createIndex({"env_broad_scale.components.label": 1})
db.env_triads.createIndex({"env_local_scale.components.label": 1})
db.env_triads.createIndex({"env_medium.components.label": 1})

// Optional: if you want to look up component labels directly
db.env_triad_component_labels.createIndex({label: 1})

const end = new Date();
print("Elapsed time: " + (end - start) + " ms");
