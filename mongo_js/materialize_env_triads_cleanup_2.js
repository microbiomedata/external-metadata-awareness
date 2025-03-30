const triadPaths = ["env_broad_scale", "env_local_scale", "env_medium"];
const redundantFields = [
    "text_annotations.digits_only",
    "text_annotations.lingering_envo",
    "text_annotations.label",
    "text_annotations.label_length",
    "text_annotations.count"
];

triadPaths.forEach(path => {
    const unsetObj = {};
    redundantFields.forEach(field => {
        unsetObj[`${path}.components.$[].${field}`] = "";
    });

    db.env_triads.updateMany(
        {[`${path}.components.text_annotations`]: {$exists: true}},
        {$unset: unsetObj}
    );
});
