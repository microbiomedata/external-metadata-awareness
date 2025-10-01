-- Create sra_biosamples_bioprojects table from SRA metadata parquet files
-- This replicates the MongoDB aggregation in extract_sra_biosample_bioproject_pairs_simple.js

-- Create table with distinct biosample-bioproject pairs
CREATE OR REPLACE TABLE sra_biosamples_bioprojects AS
SELECT DISTINCT 
    biosample AS biosample_accession,
    bioproject AS bioproject_accession
FROM read_parquet('downloads/sra_metadata_parquet/*')
WHERE biosample IS NOT NULL 
  AND bioproject IS NOT NULL
  AND biosample != ''
  AND bioproject != '';

-- Create indexes for query performance
CREATE INDEX idx_biosample ON sra_biosamples_bioprojects(biosample_accession);
CREATE INDEX idx_bioproject ON sra_biosamples_bioprojects(bioproject_accession);
CREATE INDEX idx_compound ON sra_biosamples_bioprojects(biosample_accession, bioproject_accession);

-- Show summary statistics
SELECT 
    COUNT(*) as total_pairs,
    COUNT(DISTINCT biosample_accession) as unique_biosamples,
    COUNT(DISTINCT bioproject_accession) as unique_bioprojects
FROM sra_biosamples_bioprojects;

-- Show first few records as verification
SELECT * FROM sra_biosamples_bioprojects LIMIT 10;