// Create random sample from biosamples collection and record metadata
//
// Parameters (from environment or defaults):
//   - SAMPLE_COLLECTION: Name of output collection (default: biosamples_sample_1pct)
//   - SAMPLE_PCT: Percentage to sample (default: 1)
//
// Input: biosamples collection
// Output: 
//   - Sample collection (e.g., biosamples_sample_1pct)
//   - Metadata document in notes collection

const sampleCollection = process.env.SAMPLE_COLLECTION || 'biosamples_sample_1pct';
const samplePct = parseFloat(process.env.SAMPLE_PCT || '1');
const sourceDb = process.env.SOURCE_DB || db.getName();
const sourcePort = parseInt(process.env.SOURCE_PORT || '27017');

print(`Creating ${samplePct}% sample...`);

// Calculate sample size
const totalDocs = db.biosamples.estimatedDocumentCount();
const sampleSize = Math.floor(totalDocs * samplePct / 100);
print(`Sample size: ${sampleSize} documents (${samplePct}% of ${totalDocs})`);

// Create sample using $sample aggregation
db.biosamples.aggregate([
  { $sample: { size: sampleSize } },
  { $out: sampleCollection }
]);

print(`\nRecording sample metadata...`);

// Gather statistics about the sample
const stats = db[sampleCollection].aggregate([
  {
    $addFields: {
      most_recent_date: { $max: ['$last_update', '$submission_date'] }
    }
  },
  {
    $group: {
      _id: null,
      count: { $sum: 1 },
      max_last_update: { $max: '$last_update' },
      max_submission_date: { $max: '$submission_date' },
      max_either_date: { $max: '$most_recent_date' },
      min_last_update: { $min: '$last_update' },
      min_submission_date: { $min: '$submission_date' }
    }
  }
]).toArray()[0];

// Record metadata in notes collection
db.notes.insertOne({
  collection: sampleCollection,
  created_at: new Date(),
  sample_size: stats.count,
  sample_percentage: samplePct,
  source_collection: 'biosamples',
  source_db: sourceDb,
  source_port: sourcePort,
  max_biosample_last_update: stats.max_last_update,
  max_biosample_submission_date: stats.max_submission_date,
  max_biosample_either_date: stats.max_either_date,
  min_biosample_last_update: stats.min_last_update,
  min_biosample_submission_date: stats.min_submission_date,
  note: `${samplePct}% random sample from biosamples. Most recent biosample: ${stats.max_either_date}`
});

print(`✓ Created ${sampleCollection}: ${stats.count} documents`);
print(`  Most recent biosample date: ${stats.max_either_date}`);
print(`  Metadata saved to notes collection`);
