// Cleanup temp collections from atomic biosample counting workflow
// Input: __tmp_hn_counts, __tmp_hn_totals → Output: (dropped)
// Part of atomic biosample counting workflow (Issue #237)

db.getCollection('__tmp_hn_counts').drop();
db.getCollection('__tmp_hn_totals').drop();
print('Dropped __tmp_hn_counts and __tmp_hn_totals');
