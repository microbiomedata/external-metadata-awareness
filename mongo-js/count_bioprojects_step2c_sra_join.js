// Step 2c: Join __tmp_hn_accessions with SRA and count unique bioprojects per harmonized_name
// Input: __tmp_hn_accessions + sra_biosamples_bioprojects → Output: temp_bioproject_counts

const startTime = new Date();
print(`[${startTime.toISOString()}] Step 2c: Joining with SRA and counting bioprojects`);

// Check prerequisites
const tempCount = db.getCollection("__tmp_hn_accessions").estimatedDocumentCount();
if (tempCount === 0) {
    print(`[${new Date().toISOString()}] ❌ ERROR: __tmp_hn_accessions is empty`);
    print(`[${new Date().toISOString()}] Run Step 2a first`);
    quit(1);
}
print(`[${new Date().toISOString()}] __tmp_hn_accessions has ${tempCount.toLocaleString()} records`);

const sraCount = db.sra_biosamples_bioprojects.estimatedDocumentCount();
if (sraCount === 0) {
    print(`[${new Date().toISOString()}] ❌ ERROR: sra_biosamples_bioprojects is empty`);
    print(`[${new Date().toISOString()}] Cannot count bioprojects without SRA linkage`);
    quit(1);
}
print(`[${new Date().toISOString()}] sra_biosamples_bioprojects has ${sraCount.toLocaleString()} records`);

// Verify critical indexes exist
print(`[${new Date().toISOString()}] Verifying indexes...`);
const tempIndexes = db.getCollection("__tmp_hn_accessions").getIndexes();
const hasTempIndex = tempIndexes.some(idx => idx.key.accession);
if (!hasTempIndex) {
    print(`[${new Date().toISOString()}] ❌ ERROR: __tmp_hn_accessions.accession index missing`);
    print(`[${new Date().toISOString()}] Run Step 2b first`);
    quit(1);
}
print(`[${new Date().toISOString()}] ✅ __tmp_hn_accessions.accession index exists`);

const sraIndexes = db.sra_biosamples_bioprojects.getIndexes();
const hasSraIndex = sraIndexes.some(idx => idx.key.biosample_accession);
if (!hasSraIndex) {
    print(`[${new Date().toISOString()}] ❌ ERROR: sra_biosamples_bioprojects.biosample_accession index missing`);
    print(`[${new Date().toISOString()}] This index is critical for performance`);
    quit(1);
}
print(`[${new Date().toISOString()}] ✅ sra_biosamples_bioprojects.biosample_accession index exists`);

// Check if already done
const existingCount = db.temp_bioproject_counts.estimatedDocumentCount();
if (existingCount > 0) {
    print(`[${new Date().toISOString()}] ✓ Step 2c already complete (temp_bioproject_counts has ${existingCount} records)`);
    print(`[${new Date().toISOString()}] Skipping - drop temp_bioproject_counts to rerun`);
    quit(0);
}

// Drop output collection
db.temp_bioproject_counts.drop();

print(`[${new Date().toISOString()}] Running SRA join aggregation (may take 20-40 min)...`);
db.getCollection("__tmp_hn_accessions").aggregate([
    // Lookup bioprojects via SRA linkage (fast because both collections are indexed)
    {
        $lookup: {
            from: "sra_biosamples_bioprojects",
            localField: "accession",
            foreignField: "biosample_accession",
            as: "bp"
        }
    },
    // Unwind bioproject results (may be multiple bioprojects per biosample)
    {
        $unwind: {path: "$bp", preserveNullAndEmptyArrays: false}
    },
    // Extract fields we need
    {
        $project: {
            harmonized_name: 1,
            bioproject_accession: "$bp.bioproject_accession"
        }
    },
    // Deduplicate harmonized_name + bioproject pairs
    {
        $group: {
            _id: {h: "$harmonized_name", bp: "$bioproject_accession"}
        }
    },
    // Count unique bioprojects per harmonized_name
    {
        $group: {
            _id: "$_id.h",
            unique_bioprojects_count: {$sum: 1}
        }
    },
    {
        $project: {
            harmonized_name: "$_id",
            unique_bioprojects_count: 1,
            _id: 0
        }
    },
    {
        $out: "temp_bioproject_counts"
    }
], {allowDiskUse: true});

const endTime = new Date();
const elapsed = ((endTime - startTime) / 1000).toFixed(2);
const resultCount = db.temp_bioproject_counts.countDocuments();

print(`[${endTime.toISOString()}] ✅ Step 2c complete`);
print(`[${endTime.toISOString()}] Created ${resultCount} bioproject count records`);
print(`[${endTime.toISOString()}] Elapsed: ${elapsed} seconds (${(elapsed/60).toFixed(1)} minutes)`);
