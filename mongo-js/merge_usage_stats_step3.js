// Step 3: Merge biosample and bioproject counts into harmonized_name_usage_stats
// Input: temp_biosample_counts + temp_bioproject_counts → Output: harmonized_name_usage_stats
// Part of harmonized_name usage stats workflow

print('[' + new Date().toISOString() + '] Step 3: Pre-flight checks');

const biosampleCount = db.temp_biosample_counts.estimatedDocumentCount();
if (biosampleCount === 0) {
    print('[' + new Date().toISOString() + '] ❌ ERROR: temp_biosample_counts is empty');
    print('[' + new Date().toISOString() + '] Run Step 1 first');
    quit(1);
}
print('[' + new Date().toISOString() + '] temp_biosample_counts has ' + biosampleCount.toLocaleString() + ' records');

const bioprojectCount = db.temp_bioproject_counts.estimatedDocumentCount();
if (bioprojectCount === 0) {
    print('[' + new Date().toISOString() + '] ❌ ERROR: temp_bioproject_counts is empty');
    print('[' + new Date().toISOString() + '] Run Step 2 (count-bioprojects-step2) first');
    print('[' + new Date().toISOString() + '] Refusing to merge — would silently zero every unique_bioprojects_count');
    quit(1);
}
print('[' + new Date().toISOString() + '] temp_bioproject_counts has ' + bioprojectCount.toLocaleString() + ' records');

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

const finalCount = db.harmonized_name_usage_stats.countDocuments();
print('[' + new Date().toISOString() + '] Created ' + finalCount + ' final stats');

// Post-write observation: count rows with non-zero bioproject counts. This is
// a warning (not an error) — the pre-flight check above is the real defense
// against the silent-zero failure mode in #404. Future legitimate datasets
// could in principle have zero non-zero rows; we shouldn't hard-fail on data
// distribution.
const nonZeroBioprojects = db.harmonized_name_usage_stats.countDocuments({unique_bioprojects_count: {$gt: 0}});
if (nonZeroBioprojects === 0) {
    print('[' + new Date().toISOString() + '] ⚠️  WARNING: harmonized_name_usage_stats has zero rows with unique_bioprojects_count > 0');
    print('[' + new Date().toISOString() + '] This could indicate the #404 silent-zero failure mode — verify temp_bioproject_counts before relying on the merged result.');
} else {
    print('[' + new Date().toISOString() + '] ' + nonZeroBioprojects + ' rows have unique_bioprojects_count > 0');
}

db.temp_biosample_counts.drop();
db.temp_bioproject_counts.drop();
print('[' + new Date().toISOString() + '] Cleaned up temp collections');
