db.env_triads.createIndex({ "env_broad_scale.components.text_annotations": 1 })
db.env_triads.createIndex({ "env_local_scale.components.text_annotations": 1 })
db.env_triads.createIndex({ "env_medium.components.text_annotations": 1 })

db.env_triads.createIndex({ "env_broad_scale.components.text_annotations.label": 1 })
