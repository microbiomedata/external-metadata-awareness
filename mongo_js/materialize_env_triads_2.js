const start = new Date();

const cursor = db.env_triad_component_labels.find();

while (cursor.hasNext()) {
    const doc = cursor.next();

    const updates = {
        $unset: {
            combined_coverage: ""
        },
        $rename: {
            combined_oak_envo_coverage: "combined_oak_coverage",
            oak_envo_annotations_count: "oak_annotations_count"
        },
        $set: {
            ols_annotations_count: Array.isArray(doc.ols_text_annotations) ? doc.ols_text_annotations.length : 0
        }
    };

    db.env_triad_component_labels.updateOne({_id: doc._id}, updates);
}

const end = new Date();
print("Elapsed time: " + (end - start) + " ms");

// Elapsed time: 62897 ms
// 2 minutes
