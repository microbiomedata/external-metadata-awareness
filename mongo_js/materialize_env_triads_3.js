const start = new Date();

const componentLabels = db.env_triad_component_labels.find();

while (componentLabels.hasNext()) {
    const compDoc = componentLabels.next();
    const label = compDoc.label;
    delete compDoc._id; // Optional — avoids reusing the same _id

    // Update env_broad_scale if components exist
    db.env_triads.updateMany(
        {
            "env_broad_scale.components.label": label,
            "env_broad_scale.components": {$exists: true, $ne: []}
        },
        {
            $set: {
                "env_broad_scale.components.$[b].text_annotations": compDoc
            }
        },
        {
            arrayFilters: [{"b.label": label}]
        }
    );

    // Update env_local_scale if components exist
    db.env_triads.updateMany(
        {
            "env_local_scale.components.label": label,
            "env_local_scale.components": {$exists: true, $ne: []}
        },
        {
            $set: {
                "env_local_scale.components.$[l].text_annotations": compDoc
            }
        },
        {
            arrayFilters: [{"l.label": label}]
        }
    );

    // Update env_medium if components exist
    db.env_triads.updateMany(
        {
            "env_medium.components.label": label,
            "env_medium.components": {$exists: true, $ne: []}
        },
        {
            $set: {
                "env_medium.components.$[m].text_annotations": compDoc
            }
        },
        {
            arrayFilters: [{"m.label": label}]
        }
    );
}

const end = new Date();
print("Elapsed time: " + (end - start) + " ms");
