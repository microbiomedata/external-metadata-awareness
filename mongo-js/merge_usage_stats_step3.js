// Step 3: Merge biosample and bioproject counts into harmonized_name_usage_stats
// Input: temp_biosample_counts + temp_bioproject_counts → Output: harmonized_name_usage_stats
// Part of harmonized_name usage stats workflow

// Pre-flight: refuse to merge if either input is empty.
// Closes #404 — previously merge would silently $ifNull to 0 for every bioproject_count
// when temp_bioproject_counts was empty (e.g., step 2c interrupted by mongosh
// PoolClearedOnNetworkError while server-side aggregation kept running).
const tbsCount = db.temp_biosample_counts.estimatedDocumentCount();
if (tbsCount === 0) {
    print('[' + new Date().toISOString() + '] ❌ ERROR: temp_biosample_counts is empty');
    print('[' + new Date().toISOString() + '] Step 1 (count-biosamples-step1) may not have completed');
    print('[' + new Date().toISOString() + '] Refusing to merge — would produce empty output');
    quit(1);
}
const tbpCount = db.temp_bioproject_counts.estimatedDocumentCount();
if (tbpCount === 0) {
    print('[' + new Date().toISOString() + '] ❌ ERROR: temp_bioproject_counts is empty');
    print('[' + new Date().toISOString() + '] Step 2c (count-bioprojects-step2c) may not have completed');
    print('[' + new Date().toISOString() + '] Refusing to merge — would produce all-zero unique_bioprojects_count');
    quit(1);
}
print('[' + new Date().toISOString() + '] Pre-flight passed: temp_biosample_counts=' + tbsCount + ', temp_bioproject_counts=' + tbpCount);

print('[' + new Date().toISOString() + '] Ensuring indexes exist before merge');
db.temp_bioproject_counts.createIndex({harmonized_name: 1}, {background: true});
db.temp_biosample_counts.createIndex({harmonized_name: 1}, {background: true});

print('[' + new Date().toISOString() + '] Dropping final collection');
db.harmonized_name_usage_stats.drop();

print('[' + new Date().toISOString() + '] Merging counts');
db.temp_biosample_counts.aggregate([
    {
        $lookup: {
            from: 'temp_bioproject_counts',
            localField: 'harmonized_name',
            foreignField: 'harmonized_name',
            as: 'bioproject_data'
        }
    },
    {
        $project: {
            harmonized_name: 1,
            unique_biosamples_count: 1,
            unique_bioprojects_count: {
                $ifNull: [{ $arrayElemAt: ['$bioproject_data.unique_bioprojects_count', 0] }, 0]
            }
        }
    },
    { $sort: { unique_biosamples_count: -1 } },
    { $out: 'harmonized_name_usage_stats' }
], { allowDiskUse: true });

print('[' + new Date().toISOString() + '] Created ' + db.harmonized_name_usage_stats.countDocuments() + ' final stats');

db.temp_biosample_counts.drop();
db.temp_bioproject_counts.drop();
print('[' + new Date().toISOString() + '] Cleaned up temp collections');
