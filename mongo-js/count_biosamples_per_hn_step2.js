// Step 2: Count totals and unit coverage per harmonized_name
// Input: biosamples_attributes → Output: __tmp_hn_totals
// Part of atomic biosample counting workflow (Issue #237)

const startTime = new Date();
print(`[${startTime.toISOString()}] Step 2: Counting totals and unit coverage per harmonized_name`);

// Check if already done (use getCollection for names with __)
const existingCount = db.getCollection("__tmp_hn_totals").estimatedDocumentCount();
if (existingCount > 0) {
    print(`[${new Date().toISOString()}] ✓ Step 2 already complete (__tmp_hn_totals has ${existingCount} records)`);
    print(`[${new Date().toISOString()}] Skipping - delete __tmp_hn_totals to rerun`);
    quit(0);
}

// Drop output collection
db.getCollection("__tmp_hn_totals").drop();

// Count total attributes and unit coverage per harmonized_name
print(`[${new Date().toISOString()}] Running aggregation (may take 15-30 min for 712M records)...`);
db.biosamples_attributes.aggregate([
    {
        $match: {
            harmonized_name: { $type: "string", $ne: "" }
        }
    },
    {
        $group: {
            _id: "$harmonized_name",
            total_attribute_records: { $sum: 1 },
            has_unit_records: {
                $sum: {
                    $cond: [
                        {
                            $and: [
                                { $ne: [{ $type: "$unit" }, "null"] },
                                { $ne: [{ $type: "$unit" }, "missing"] },
                                { $ne: ["$unit", ""] }
                            ]
                        },
                        1,
                        0
                    ]
                }
            }
        }
    },
    {
        $project: {
            _id: 0,
            harmonized_name: "$_id",
            total_attribute_records: 1,
            has_unit_records: 1,
            unit_coverage_percent: {
                $cond: [
                    { $gt: ["$total_attribute_records", 0] },
                    {
                        $round: [
                            {
                                $multiply: [
                                    {
                                        $divide: [
                                            "$has_unit_records",
                                            "$total_attribute_records"
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
        $out: "__tmp_hn_totals"
    }
], { allowDiskUse: true });

const endTime = new Date();
const elapsed = ((endTime - startTime) / 1000).toFixed(2);
const resultCount = db.getCollection("__tmp_hn_totals").countDocuments();

print(`[${endTime.toISOString()}] ✅ Step 2 complete`);
print(`[${endTime.toISOString()}] Created ${resultCount} records in __tmp_hn_totals`);
print(`[${endTime.toISOString()}] Elapsed: ${elapsed} seconds`);
