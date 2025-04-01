const start = new Date();

const inScope = db.env_triad_component_in_scope_curies_lc.find();

while (inScope.hasNext()) {
    const clsDoc = inScope.next();
    const curie_lc = clsDoc.curie_lc;

    // Remove _id so it doesn't cause conflicts when inserting
    delete clsDoc._id;

    // Update env_broad_scale
    db.env_triads.updateMany(
        {"env_broad_scale.components.curie_lc": curie_lc},
        {
            $set: {
                "env_broad_scale.components.$[b].asserted_class": clsDoc
            }
        },
        {
            arrayFilters: [{"b.curie_lc": curie_lc}]
        }
    );

    // Update env_local_scale
    db.env_triads.updateMany(
        {"env_local_scale.components.curie_lc": curie_lc},
        {
            $set: {
                "env_local_scale.components.$[l].asserted_class": clsDoc
            }
        },
        {
            arrayFilters: [{"l.curie_lc": curie_lc}]
        }
    );

    // Update env_medium
    db.env_triads.updateMany(
        {"env_medium.components.curie_lc": curie_lc},
        {
            $set: {
                "env_medium.components.$[m].asserted_class": clsDoc
            }
        },
        {
            arrayFilters: [{"m.curie_lc": curie_lc}]
        }
    );
}

const end = new Date();
print("Elapsed time: " + (end - start) + " ms");
