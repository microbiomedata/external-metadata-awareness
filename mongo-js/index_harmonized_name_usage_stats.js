// Create indexes on harmonized_name_usage_stats for efficient querying
// Input: harmonized_name_usage_stats → Output: (indexed)

print('[' + new Date().toISOString() + '] Creating index on harmonized_name');
try { db.harmonized_name_usage_stats.createIndex({harmonized_name: 1}, {background: true}); } catch(e) { print('harmonized_name index exists: ' + e.message); }

print('[' + new Date().toISOString() + '] Creating index on unique_biosamples_count');
try { db.harmonized_name_usage_stats.createIndex({unique_biosamples_count: 1}, {background: true}); } catch(e) { print('biosamples_count index exists: ' + e.message); }

print('[' + new Date().toISOString() + '] Creating index on unique_bioprojects_count');
try { db.harmonized_name_usage_stats.createIndex({unique_bioprojects_count: 1}, {background: true}); } catch(e) { print('bioprojects_count index exists: ' + e.message); }

print('[' + new Date().toISOString() + '] Creating compound index for sorting/filtering');
try { db.harmonized_name_usage_stats.createIndex({unique_biosamples_count: -1, unique_bioprojects_count: -1}, {background: true}); } catch(e) { print('compound index exists: ' + e.message); }

print('[' + new Date().toISOString() + '] All indexes created successfully');
