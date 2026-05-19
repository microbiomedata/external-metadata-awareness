// Aggregate distinct (harmonized_name, content) pairs with biosample counts
// Input: biosamples_attributes → Output: content_pairs_aggregated
// Mirrors the K-BERDL nmdc_ncbi_biosamples.content_pairs_aggregated table.
// Closes #405

const startTime = new Date();
print(`[${startTime.toISOString()}] Aggregating (harmonized_name, content) pairs`);

// Check if already done
const existingCount = db.content_pairs_aggregated.estimatedDocumentCount();
if (existingCount > 0) {
    print(`[${new Date().toISOString()}] ✓ content_pairs_aggregated has ${existingCount} records`);
    print(`[${new Date().toISOString()}] Skipping - drop content_pairs_aggregated to rerun`);
    quit(0);
}

// Verify source collection has data
const srcCount = db.biosamples_attributes.estimatedDocumentCount();
if (srcCount === 0) {
    print(`[${new Date().toISOString()}] ❌ ERROR: biosamples_attributes is empty`);
    quit(1);
}
print(`[${new Date().toISOString()}] biosamples_attributes has ${srcCount.toLocaleString()} records`);

// Drop and rebuild
db.content_pairs_aggregated.drop();

// Two-stage group: first dedupe (h, c, a), then count distinct accessions per (h, c).
// Same pattern as count_biosamples_usage_stats_step1.js — avoids $addToSet memory limit.
print(`[${new Date().toISOString()}] Running aggregation (may take 30-90 min for 800M+ records)...`);
db.biosamples_attributes.aggregate([
    {
        $match: {
            harmonized_name: {$exists: true, $ne: "", $ne: null},
            content: {$exists: true, $ne: "", $ne: null},
            accession: {$exists: true, $ne: "", $ne: null}
        }
    },
    // First $group: deduplicate (harmonized_name, content, accession) triples
    {
        $group: {
            _id: {h: "$harmonized_name", c: "$content", a: "$accession"}
        }
    },
    // Second $group: count unique accessions per (harmonized_name, content)
    {
        $group: {
            _id: {h: "$_id.h", c: "$_id.c"},
            biosample_count: {$sum: 1}
        }
    },
    {
        $project: {
            harmonized_name: "$_id.h",
            content: "$_id.c",
            biosample_count: 1,
            _id: 0
        }
    },
    {
        $out: "content_pairs_aggregated"
    }
], {allowDiskUse: true});

const aggEnd = new Date();
const resultCount = db.content_pairs_aggregated.countDocuments();
print(`[${aggEnd.toISOString()}] Aggregation complete: ${resultCount.toLocaleString()} (harmonized_name, content) pairs`);

// Indexes
print(`[${new Date().toISOString()}] Creating indexes on content_pairs_aggregated...`);
db.content_pairs_aggregated.createIndex({harmonized_name: 1}, {background: true});
db.content_pairs_aggregated.createIndex({biosample_count: -1}, {background: true});

const endTime = new Date();
const elapsed = ((endTime - startTime) / 1000).toFixed(2);
print(`[${endTime.toISOString()}] ✅ Complete in ${elapsed}s (${(elapsed/60).toFixed(1)} minutes)`);
