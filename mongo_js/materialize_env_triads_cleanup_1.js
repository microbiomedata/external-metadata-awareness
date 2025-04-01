const triadPaths = ["env_broad_scale", "env_local_scale", "env_medium"];

triadPaths.forEach(path => {
    db.env_triads.updateMany(
        {[`${path}.components.text_annotations.label`]: {$exists: true}},
        {
            $unset: {
                [`${path}.components.$[].text_annotations.label`]: ""
            }
        }
    );

    db.env_triads.updateMany(
        {[`${path}.components.asserted_class.label`]: {$exists: true}},
        {
            $unset: {
                [`${path}.components.$[].asserted_class.label`]: ""
            }
        }
    );
});
