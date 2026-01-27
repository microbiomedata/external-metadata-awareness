// Count usage of each harmonized field in biosamples_flattened collection
// Input: biosamples_flattened → Output: biosamples_flattened_field_counts

print("[" + new Date().toISOString() + "] Starting harmonized field usage counting...")
print("[" + new Date().toISOString() + "] Input collection: biosamples_flattened")

// Get baseline count
var totalBiosamples = db.biosamples_flattened.countDocuments({})
print("[" + new Date().toISOString() + "] Total biosamples: " + totalBiosamples.toLocaleString())

// Convert each document to field-value pairs and count usage
db.biosamples_flattened.aggregate([
    // Convert document to key-value array 
    {
        $project: {
            accession: 1,
            kvArray: { $objectToArray: "$$ROOT" }
        }
    },
    // Unwind to get individual fields
    { 
        $unwind: "$kvArray" 
    },
    // Filter out system fields and null/empty values
    { 
        $match: { 
            "kvArray.k": { $nin: ["_id", "accession"] },
            "kvArray.v": { $ne: null, $ne: "", $exists: true }
        } 
    },
    // Count usage per harmonized field name
    {
        $group: {
            _id: "$kvArray.k",
            biosample_count: { $sum: 1 },
            sample_accessions: { $addToSet: "$accession" }
        }
    },
    // Calculate coverage statistics
    {
        $project: {
            _id: 0,
            harmonized_name: "$_id",
            biosample_count: 1,
            unique_accessions: { $size: "$sample_accessions" },
            coverage_percent: {
                $round: [{
                    $multiply: [
                        { $divide: ["$biosample_count", totalBiosamples] },
                        100
                    ]
                }, 2]
            }
        }
    },
    // Sort by usage frequency
    {
        $sort: { biosample_count: -1 }
    },
    // Save results
    {
        $out: "biosamples_flattened_field_counts"
    }
])

// Generate summary statistics
var totalFields = db.biosamples_flattened_field_counts.countDocuments({})
var totalUsages = db.biosamples_flattened_field_counts.aggregate([
    {$group: {_id: null, total: {$sum: "$biosample_count"}}}
]).next().total

print("[" + new Date().toISOString() + "] ✅ Field usage counting complete")
print("[" + new Date().toISOString() + "] Unique harmonized fields: " + totalFields.toLocaleString())
print("[" + new Date().toISOString() + "] Total field usages: " + totalUsages.toLocaleString())
print("[" + new Date().toISOString() + "] Average fields per biosample: " + (totalUsages/totalBiosamples).toFixed(1))
print("[" + new Date().toISOString() + "] Collection created: biosamples_flattened_field_counts")