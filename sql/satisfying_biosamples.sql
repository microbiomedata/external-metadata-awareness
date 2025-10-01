-- Query for biosamples that satisfy all criteria
-- Criteria:
--   - collection_date IS NOT NULL
--   - lat_lon IS NOT NULL
--   - Exactly one of each environmental triad component
--   - env_broad_scale must use ENVO prefix
--   - env_local_scale must use ENVO or PO prefix
--   - env_medium must use ENVO or PO prefix

WITH single_triad_samples AS (
  SELECT accession
  FROM env_triads_flattened
  GROUP BY accession
  HAVING
    COUNT(CASE WHEN attribute = 'env_broad_scale' THEN 1 END) = 1
    AND COUNT(CASE WHEN attribute = 'env_local_scale' THEN 1 END) = 1
    AND COUNT(CASE WHEN attribute = 'env_medium' THEN 1 END) = 1
)
SELECT
  bf.accession,
  bf.collection_date,
  bf.lat_lon,
  etf_broad.id as env_broad_scale,
  etf_local.id as env_local_scale,
  etf_medium.id as env_medium
FROM biosamples_flattened bf
INNER JOIN single_triad_samples sts ON bf.accession = sts.accession
LEFT JOIN env_triads_flattened etf_broad
  ON bf.accession = etf_broad.accession AND etf_broad.attribute = 'env_broad_scale'
LEFT JOIN env_triads_flattened etf_local
  ON bf.accession = etf_local.accession AND etf_local.attribute = 'env_local_scale'
LEFT JOIN env_triads_flattened etf_medium
  ON bf.accession = etf_medium.accession AND etf_medium.attribute = 'env_medium'
WHERE
  bf.collection_date IS NOT NULL
  AND bf.lat_lon IS NOT NULL
  AND etf_broad.prefix = 'ENVO'
  AND (etf_local.prefix = 'ENVO' OR etf_local.prefix = 'PO')
  AND (etf_medium.prefix = 'ENVO' OR etf_medium.prefix = 'PO')
ORDER BY bf.accession;
