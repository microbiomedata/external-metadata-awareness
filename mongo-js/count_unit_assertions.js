// Count harmonized_name + unit combinations with explicit unit assertions
// Input: biosamples_attributes → Output: unit_assertion_counts

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting unit assertion counting`);

// Create beneficial indexes (error tolerant)
print(`[${new Date().toISOString()}] Ensuring beneficial indexes exist`);
try {
    db.biosamples_attributes.createIndex({unit: 1}, {background: true});
} catch(e) {
    print(`Unit index exists: ${e.message}`);
}
try {
    db.biosamples_attributes.createIndex({harmonized_name: 1}, {background: true});
} catch(e) {
    print(`Harmonized_name index exists: ${e.message}`);
}
try {
    db.biosamples_attributes.createIndex({unit: 1, harmonized_name: 1}, {background: true});
} catch(e) {
    print(`Compound unit+harmonized_name index exists: ${e.message}`);
}

// Drop output collection
db.unit_assertion_counts.drop();

// Basic counting aggregation
db.biosamples_attributes.aggregate([
    {
        $match: {
            unit: { $exists: true, $ne: null, $ne: "" },
            harmonized_name: { $exists: true, $ne: null }
        }
    },
    {
        $group: {
            _id: {
                harmonized_name: "$harmonized_name",
                unit: "$unit"
            },
            count: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            harmonized_name: "$_id.harmonized_name",
            unit: "$_id.unit",
            count: 1
        }
    },
    {
        $sort: { count: -1 }
    },
    {
        $out: "unit_assertion_counts"
    }
], { allowDiskUse: true });

const resultCount = db.unit_assertion_counts.countDocuments();
print(`[${new Date().toISOString()}] Created ${resultCount} harmonized_name + unit combinations`);

// Create indexes on output collection for efficient querying
print(`[${new Date().toISOString()}] Creating indexes on output collection`);
try {
    db.unit_assertion_counts.createIndex({harmonized_name: 1}, {background: true});
} catch(e) {
    print(`Output harmonized_name index exists: ${e.message}`);
}
try {
    db.unit_assertion_counts.createIndex({count: -1}, {background: true});
} catch(e) {
    print(`Output count index exists: ${e.message}`);
}
try {
    db.unit_assertion_counts.createIndex({unit: 1}, {background: true});
} catch(e) {
    print(`Output unit index exists: ${e.message}`);
}

const endTime = new Date();
print(`[${endTime.toISOString()}] Completed in ${((endTime - startTime)/1000).toFixed(2)} seconds`);