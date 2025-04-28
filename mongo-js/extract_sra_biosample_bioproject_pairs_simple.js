/**
 * Simple script to extract biosample-bioproject pairs from SRA metadata.
 */

print(`[${new Date().toISOString()}] Starting extraction of biosample-bioproject pairs`);

// First drop the existing collection to start fresh
print(`[${new Date().toISOString()}] Dropping existing sra_biosamples_bioprojects collection`);
db.sra_biosamples_bioprojects.drop();

// Create the collection with unique index
print(`[${new Date().toISOString()}] Creating unique compound index`);
db.sra_biosamples_bioprojects.createIndex(
    { biosample_accession: 1, bioproject_accession: 1 },
    { unique: true }
);

// Single aggregation to extract pairs and save to new collection
print(`[${new Date().toISOString()}] Running aggregation to extract pairs`);
db.sra_metadata.aggregate([
    // Match documents with both biosample and bioproject fields
    { $match: { 
        biosample: { $exists: true, $ne: null },
        bioproject: { $exists: true, $ne: null }
    }},
    
    // Project just what we need
    { $project: {
        _id: 0,
        biosample_accession: "$biosample",
        bioproject_accession: "$bioproject"
    }},
    
    // Group to get distinct pairs
    { $group: {
        _id: { 
            biosample: "$biosample_accession", 
            bioproject: "$bioproject_accession" 
        },
        biosample_accession: { $first: "$biosample_accession" },
        bioproject_accession: { $first: "$bioproject_accession" }
    }},
    
    // Final format
    { $project: {
        _id: 0,
        biosample_accession: 1,
        bioproject_accession: 1
    }},
    
    // Write results to a new collection
    { $out: "sra_biosamples_bioprojects" }
], { allowDiskUse: true });

// Create additional indexes for query performance
print(`[${new Date().toISOString()}] Creating individual field indexes`);
db.sra_biosamples_bioprojects.createIndex({ biosample_accession: 1 });
db.sra_biosamples_bioprojects.createIndex({ bioproject_accession: 1 });

// Count the final results
const totalPairs = db.sra_biosamples_bioprojects.countDocuments();
print(`[${new Date().toISOString()}] Extraction complete! Found ${totalPairs.toLocaleString()} unique biosample-bioproject pairs`);