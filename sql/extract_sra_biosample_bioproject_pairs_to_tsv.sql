-- Extract biosample-bioproject pairs from SRA parquet files and export to TSV
-- This script creates a view over SRA parquet files, extracts distinct pairs, and exports to TSV

-- Create view over SRA parquet files
CREATE OR REPLACE VIEW sra AS 
SELECT * FROM read_parquet('local/sra_metadata_parquet/*');

-- Create table with distinct biosample-bioproject pairs
CREATE OR REPLACE TABLE sra_biosamples_bioprojects AS
SELECT DISTINCT 
    biosample,
    bioproject
FROM sra 
WHERE biosample IS NOT NULL 
  AND bioproject IS NOT NULL
  AND biosample != ''
  AND bioproject != '';

-- Show summary statistics
SELECT 
    COUNT(*) as total_pairs,
    COUNT(DISTINCT biosample) as unique_biosamples,
    COUNT(DISTINCT bioproject) as unique_bioprojects
FROM sra_biosamples_bioprojects;

-- Export to TSV file
COPY sra_biosamples_bioprojects TO 'local/sra_biosample_bioproject_pairs.tsv' 
(FORMAT CSV, DELIMITER E'\t', HEADER);

-- Show first few records for verification
SELECT * FROM sra_biosamples_bioprojects LIMIT 10;