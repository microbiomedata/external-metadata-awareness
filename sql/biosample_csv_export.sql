-- Biosample CSV Export Query
-- Goal: One row per biosample with accession, collection_date, lat, lon, and environmental triads

-- Step 1: Test basic structure - get biosamples with collection_date and lat_lon
-- Uncomment to test:
-- SELECT
--     accession,
--     collection_date,
--     lat_lon
-- FROM biosamples_flattened
-- WHERE collection_date IS NOT NULL
--   AND lat_lon IS NOT NULL
-- LIMIT 10;

-- Step 2: Join with env_triads for one attribute (env_medium)
-- Uncomment to test:
-- SELECT
--     bf.accession,
--     bf.collection_date,
--     bf.lat_lon,
--     etf.id as env_medium_id,
--     etf.label as env_medium_label
-- FROM biosamples_flattened bf
-- LEFT JOIN env_triads_flattened etf
--   ON bf.accession = etf.accession
--   AND etf.attribute = 'env_medium'
-- WHERE bf.collection_date IS NOT NULL
--   AND bf.lat_lon IS NOT NULL
-- LIMIT 10;

-- Step 3: Join all three environmental triads
-- Uncomment to test:
-- SELECT
--     bf.accession,
--     bf.collection_date,
--     bf.lat_lon,
--     etf_broad.id as env_broad_scale_id,
--     etf_broad.label as env_broad_scale_label,
--     etf_local.id as env_local_scale_id,
--     etf_local.label as env_local_scale_label,
--     etf_medium.id as env_medium_id,
--     etf_medium.label as env_medium_label
-- FROM biosamples_flattened bf
-- LEFT JOIN env_triads_flattened etf_broad
--   ON bf.accession = etf_broad.accession
--   AND etf_broad.attribute = 'env_broad_scale'
-- LEFT JOIN env_triads_flattened etf_local
--   ON bf.accession = etf_local.accession
--   AND etf_local.attribute = 'env_local_scale'
-- LEFT JOIN env_triads_flattened etf_medium
--   ON bf.accession = etf_medium.accession
--   AND etf_medium.attribute = 'env_medium'
-- WHERE bf.collection_date IS NOT NULL
--   AND bf.lat_lon IS NOT NULL
-- LIMIT 10;

-- Step 4: Check for samples with multiple env triad values
-- This will show how many values each sample has for each attribute
-- Uncomment to test:
SELECT
    accession,
    COUNT(CASE WHEN attribute = 'env_broad_scale' THEN 1 END) as broad_count,
    COUNT(CASE WHEN attribute = 'env_local_scale' THEN 1 END) as local_count,
    COUNT(CASE WHEN attribute = 'env_medium' THEN 1 END) as medium_count
FROM env_triads_flattened
GROUP BY accession
HAVING broad_count > 1 OR local_count > 1 OR medium_count > 1
LIMIT 20;

-- Step 5: Filter to samples with exactly 1 value for each env triad
-- (Coming next after we see Step 4 results)

-- Step 6: Parse lat_lon into separate lat and lon columns
-- (Coming next - need to see lat_lon format first)
