// Step 3: Merge biosample and bioproject counts into harmonized_name_usage_stats
// Input: temp_biosample_counts + temp_bioproject_counts → Output: harmonized_name_usage_stats
// Part of harmonized_name usage stats workflow

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
