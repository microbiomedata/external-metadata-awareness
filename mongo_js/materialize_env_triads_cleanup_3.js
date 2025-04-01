const triadPaths = ["env_broad_scale", "env_local_scale", "env_medium"];
const redundantFields = [
    "asserted_class.prefix",
    "asserted_class.curie_lc",
    "asserted_class.uses_obo_prefix",
    "asserted_class.uses_bioportal_prefix"
];

triadPaths.forEach(path => {
    const unsetObj = {};
    redundantFields.forEach(field => {
        unsetObj[`${path}.components.$[].${field}`] = "";
    });

    db.env_triads.updateMany(
        {[`${path}.components.asserted_class`]: {$exists: true}},
        {$unset: unsetObj}
    );
});
