// Count harmonized_name combinations with mixed letter/number content  
// Input: biosamples_attributes → Output: mixed_content_counts

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting mixed content counting`);

// Create beneficial indexes (error tolerant)
print(`[${new Date().toISOString()}] Ensuring beneficial indexes exist`);
try {
    db.biosamples_attributes.createIndex({content: 1}, {background: true});
} catch(e) {
    print(`Content index exists: ${e.message}`);
}
try {
    db.biosamples_attributes.createIndex({harmonized_name: 1}, {background: true});
} catch(e) {
    print(`Harmonized_name index exists: ${e.message}`);
}

// Drop output collection
db.mixed_content_counts.drop();

// Basic counting aggregation
db.biosamples_attributes.aggregate([
    {
        $match: {
            content: { $regex: ".*[0-9].*[a-zA-Z].*|.*[a-zA-Z].*[0-9].*" }
        }
    },
    {
        $group: {
            _id: "$harmonized_name",
            count: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            harmonized_name: "$_id",
            count: 1
        }
    },
    {
        $sort: { count: -1 }
    },
    {
        $out: "mixed_content_counts"
    }
], { allowDiskUse: true });

const resultCount = db.mixed_content_counts.countDocuments();
print(`[${new Date().toISOString()}] Created ${resultCount} harmonized_name records with mixed content`);

// Create indexes on output collection for efficient querying
print(`[${new Date().toISOString()}] Creating indexes on output collection`);
try {
    db.mixed_content_counts.createIndex({harmonized_name: 1}, {background: true});
} catch(e) {
    print(`Output harmonized_name index exists: ${e.message}`);
}
try {
    db.mixed_content_counts.createIndex({count: -1}, {background: true});
} catch(e) {
    print(`Output count index exists: ${e.message}`);
}

const endTime = new Date();
print(`[${endTime.toISOString()}] Completed in ${((endTime - startTime)/1000).toFixed(2)} seconds`);