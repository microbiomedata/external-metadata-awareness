// Count attribute_name + harmonized_name pairings
// Input: biosamples_attributes → Output: attribute_harmonized_pairings

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting attribute_name + harmonized_name pairing counts`);

// Create beneficial indexes (error tolerant)
print(`[${new Date().toISOString()}] Ensuring beneficial indexes exist`);
try {
    db.biosamples_attributes.createIndex({attribute_name: 1}, {background: true});
} catch(e) {
    print(`Attribute_name index exists: ${e.message}`);
}
try {
    db.biosamples_attributes.createIndex({harmonized_name: 1}, {background: true});
} catch(e) {
    print(`Harmonized_name index exists: ${e.message}`);
}
try {
    db.biosamples_attributes.createIndex({attribute_name: 1, harmonized_name: 1}, {background: true});
} catch(e) {
    print(`Compound attribute_name+harmonized_name index exists: ${e.message}`);
}

// Drop output collection
db.attribute_harmonized_pairings.drop();

// Count attribute_name + harmonized_name combinations
db.biosamples_attributes.aggregate([
    {
        $group: {
            _id: {
                attribute_name: "$attribute_name",
                harmonized_name: "$harmonized_name"
            },
            count: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            attribute_name: "$_id.attribute_name",
            harmonized_name: "$_id.harmonized_name",
            count: 1
        }
    },
    {
        $sort: { count: -1 }
    },
    {
        $out: "attribute_harmonized_pairings"
    }
], { allowDiskUse: true });

const resultCount = db.attribute_harmonized_pairings.countDocuments();
print(`[${new Date().toISOString()}] Created ${resultCount} attribute_name + harmonized_name pairing records`);

// Create indexes on output collection for efficient querying
print(`[${new Date().toISOString()}] Creating indexes on output collection`);
try {
    db.attribute_harmonized_pairings.createIndex({attribute_name: 1}, {background: true});
} catch(e) {
    print(`Output attribute_name index exists: ${e.message}`);
}
try {
    db.attribute_harmonized_pairings.createIndex({harmonized_name: 1}, {background: true});
} catch(e) {
    print(`Output harmonized_name index exists: ${e.message}`);
}
try {
    db.attribute_harmonized_pairings.createIndex({count: -1}, {background: true});
} catch(e) {
    print(`Output count index exists: ${e.message}`);
}
try {
    db.attribute_harmonized_pairings.createIndex({attribute_name: 1, harmonized_name: 1}, {background: true});
} catch(e) {
    print(`Output compound index exists: ${e.message}`);
}

const endTime = new Date();
print(`[${endTime.toISOString()}] Completed in ${((endTime - startTime)/1000).toFixed(2)} seconds`);