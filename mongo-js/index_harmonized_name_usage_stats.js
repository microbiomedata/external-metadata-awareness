// Create indexes on harmonized_name_usage_stats for efficient querying
// Input: harmonized_name_usage_stats → Output: (indexed)

print('[' + new Date().toISOString() + '] Creating index on harmonized_name');
db.harmonized_name_usage_stats.createIndex({harmonized_name: 1}, {background: true});

print('[' + new Date().toISOString() + '] Creating index on unique_biosamples_count');
db.harmonized_name_usage_stats.createIndex({unique_biosamples_count: 1}, {background: true});

print('[' + new Date().toISOString() + '] Creating index on unique_bioprojects_count');
db.harmonized_name_usage_stats.createIndex({unique_bioprojects_count: 1}, {background: true});

print('[' + new Date().toISOString() + '] Creating compound index for sorting/filtering');
db.harmonized_name_usage_stats.createIndex({unique_biosamples_count: -1, unique_bioprojects_count: -1}, {background: true});

print('[' + new Date().toISOString() + '] All indexes created successfully');
