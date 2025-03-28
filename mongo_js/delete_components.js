db.biosamples_env_triad_value_counts_gt_1.updateMany(
    {}, // match all documents
    {$unset: {components: "", components_count: ""}} // remove these fields
)