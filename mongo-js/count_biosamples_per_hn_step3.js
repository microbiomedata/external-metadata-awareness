// Step 3: Join temp tables and create final harmonized_name_biosample_counts collection
// Input: __tmp_hn_counts + __tmp_hn_totals → Output: harmonized_name_biosample_counts
// Part of atomic biosample counting workflow (Issue #237)

const startTime = new Date();
print(`[${startTime.toISOString()}] Step 3: Joining temp tables and creating final collection`);

// Check if already done
const existingCount = db.harmonized_name_biosample_counts.estimatedDocumentCount();
if (existingCount > 0) {
    print(`[${new Date().toISOString()}] ✓ Step 3 already complete (harmonized_name_biosample_counts has ${existingCount} records)`);
    print(`[${new Date().toISOString()}] Skipping - delete harmonized_name_biosample_counts to rerun`);
    quit(0);
}

// Check prerequisites
const countsExist = db.__tmp_hn_counts.estimatedDocumentCount();
const totalsExist = db.__tmp_hn_totals.estimatedDocumentCount();

if (countsExist === 0) {
    print(`[${new Date().toISOString()}] ERROR: __tmp_hn_counts is empty - run Step 1 first`);
    quit(1);
}
if (totalsExist === 0) {
    print(`[${new Date().toISOString()}] ERROR: __tmp_hn_totals is empty - run Step 2 first`);
    quit(1);
}

print(`[${new Date().toISOString()}] Prerequisites met (__tmp_hn_counts: ${countsExist}, __tmp_hn_totals: ${totalsExist})`);

// Get total unique accessions for coverage calculation
print(`[${new Date().toISOString()}] Calculating total unique accessions...`);
const totalUniqueAccessions = db.biosamples_attributes.aggregate([
    { $match: { accession: { $type: "string", $ne: "" } } },
    { $group: { _id: "$accession" } },
    { $count: "total" }
], { allowDiskUse: true }).toArray()[0]?.total ?? 0;

print(`[${new Date().toISOString()}] Total unique accessions: ${totalUniqueAccessions.toLocaleString()}`);

// Drop output collection
db.harmonized_name_biosample_counts.drop();

// Join temp tables
print(`[${new Date().toISOString()}] Joining temp tables (may take 5-10 min)...`);
db.__tmp_hn_counts.aggregate([
    {
        $lookup: {
            from: "__tmp_hn_totals",
            localField: "harmonized_name",
            foreignField: "harmonized_name",
            as: "t"
        }
    },
    {
        $unwind: {
            path: "$t",
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $addFields: {
            total_attribute_records: "$t.total_attribute_records",
            has_unit_records: "$t.has_unit_records",
            unit_coverage_percent: "$t.unit_coverage_percent",
            coverage_percent: {
                $cond: [
                    { $gt: [totalUniqueAccessions, 0] },
                    {
                        $round: [
                            {
                                $multiply: [
                                    {
                                        $divide: [
                                            "$biosample_count",
                                            totalUniqueAccessions
                                        ]
                                    },
                                    100
                                ]
                            },
                            2
                        ]
                    },
                    0
                ]
            }
        }
    },
    {
        $project: {
            t: 0
        }
    },
    {
        $sort: {
            biosample_count: -1
        }
    },
    {
        $out: "harmonized_name_biosample_counts"
    }
], { allowDiskUse: true });

// Create indexes
print(`[${new Date().toISOString()}] Creating indexes on harmonized_name_biosample_counts...`);
db.harmonized_name_biosample_counts.createIndex({ harmonized_name: 1 });
db.harmonized_name_biosample_counts.createIndex({ biosample_count: -1 });
db.harmonized_name_biosample_counts.createIndex({ unit_coverage_percent: -1 });

const endTime = new Date();
const elapsed = ((endTime - startTime) / 1000).toFixed(2);
const resultCount = db.harmonized_name_biosample_counts.countDocuments();

print(`[${endTime.toISOString()}] ✅ Step 3 complete`);
print(`[${endTime.toISOString()}] Created harmonized_name_biosample_counts with ${resultCount} records`);
print(`[${endTime.toISOString()}] Elapsed: ${elapsed} seconds`);
