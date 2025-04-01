// For text_annotations.label existence checks
db.env_triads.createIndex({"env_broad_scale.components.text_annotations.label": 1})
db.env_triads.createIndex({"env_local_scale.components.text_annotations.label": 1})
db.env_triads.createIndex({"env_medium.components.text_annotations.label": 1})

// For asserted_class.label existence checks
db.env_triads.createIndex({"env_broad_scale.components.asserted_class.label": 1})
db.env_triads.createIndex({"env_local_scale.components.asserted_class.label": 1})
db.env_triads.createIndex({"env_medium.components.asserted_class.label": 1})
