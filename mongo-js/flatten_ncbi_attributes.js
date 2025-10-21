// Flatten NCBI attributes collection directly in MongoDB
// Input: attributes (nested NCBI attribute documents)
// Output: ncbi_attributes_flattened (flat documents with concatenated packages/synonyms)

const startTime = new Date();
print(`[${startTime.toISOString()}] Starting NCBI attributes collection flattening`);

// Create beneficial indexes (error tolerant)
print(`[${new Date().toISOString()}] Ensuring beneficial indexes exist`);
try {
    db.attributes.createIndex({HarmonizedName: 1}, {background: true});
} catch(e) {
    print(`Attributes HarmonizedName index exists: ${e.message}`);
}

// Drop output collection
db.ncbi_attributes_flattened.drop();

// Flatten attributes using aggregation
print(`[${new Date().toISOString()}] Flattening attributes collection...`);
db.attributes.aggregate([
    {
        $project: {
            _id: 0,
            // Basic attribute info
            name: "$Name.content",
            harmonized_name: "$HarmonizedName.content",
            description: "$Description.content",
            format: "$Format.content",
            
            // Concatenated synonyms (sorted)
            synonyms: {
                $reduce: {
                    input: {
                        $sortArray: {
                            input: {
                                $map: {
                                    input: { 
                                        $cond: {
                                            if: { $isArray: "$Synonym" },
                                            then: "$Synonym",
                                            else: []
                                        }
                                    },
                                    as: "syn",
                                    in: "$$syn.content"
                                }
                            },
                            sortBy: 1
                        }
                    },
                    initialValue: "",
                    in: {
                        $cond: {
                            if: { $eq: ["$$value", ""] },
                            then: "$$this",
                            else: { $concat: ["$$value", "; ", "$$this"] }
                        }
                    }
                }
            },
            
            // Concatenated packages (sorted)
            packages: {
                $reduce: {
                    input: {
                        $sortArray: {
                            input: {
                                $map: {
                                    input: { 
                                        $cond: {
                                            if: { $isArray: "$Package" },
                                            then: "$Package",
                                            else: []
                                        }
                                    },
                                    as: "pkg",
                                    in: "$$pkg.content"
                                }
                            },
                            sortBy: 1
                        }
                    },
                    initialValue: "",
                    in: {
                        $cond: {
                            if: { $eq: ["$$value", ""] },
                            then: "$$this",
                            else: { $concat: ["$$value", "; ", "$$this"] }
                        }
                    }
                }
            }
        }
    },
    {
        $out: "ncbi_attributes_flattened"
    }
], { allowDiskUse: true });

const resultCount = db.ncbi_attributes_flattened.countDocuments();
print(`[${new Date().toISOString()}] Created ${resultCount} flattened attribute records`);

// Create indexes on output collection
print(`[${new Date().toISOString()}] Creating indexes on flattened collection`);
try {
    db.ncbi_attributes_flattened.createIndex({harmonized_name: 1}, {background: true});
} catch(e) {
    print(`Flattened harmonized_name index exists: ${e.message}`);
}
try {
    db.ncbi_attributes_flattened.createIndex({name: 1}, {background: true});
} catch(e) {
    print(`Flattened name index exists: ${e.message}`);
}
try {
    db.ncbi_attributes_flattened.createIndex({format: 1}, {background: true});
} catch(e) {
    print(`Format index exists: ${e.message}`);
}

// Show sample results
print(`[${new Date().toISOString()}] Sample flattened attributes:`);
db.ncbi_attributes_flattened.find().limit(3).forEach(attr => {
    print(`  ${attr.harmonized_name} (${attr.name}): ${attr.format || 'no format'}`);
    if (attr.synonyms) print(`    Synonyms: ${attr.synonyms.substring(0, 50)}...`);
});

const endTime = new Date();
print(`[${endTime.toISOString()}] Completed in ${((endTime - startTime)/1000).toFixed(2)} seconds`);