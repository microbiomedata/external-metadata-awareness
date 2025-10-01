-- Combined query for all bioprojects with biosample counts and bioproject metadata
-- Includes satisfaction rate (satisfying_biosamples / biosamples_with_attributes)

WITH single_triad_samples AS (
  SELECT accession
  FROM env_triads_flattened
  GROUP BY accession
  HAVING
    COUNT(CASE WHEN attribute = 'env_broad_scale' THEN 1 END) = 1
    AND COUNT(CASE WHEN attribute = 'env_local_scale' THEN 1 END) = 1
    AND COUNT(CASE WHEN attribute = 'env_medium' THEN 1 END) = 1
),
satisfying_biosamples AS (
  SELECT DISTINCT bf.accession
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
),
biosamples_with_attributes AS (
  SELECT DISTINCT accession
  FROM biosamples_attributes
),
bioproject_counts AS (
  SELECT
    sbp.bioproject_accession,
    COUNT(DISTINCT sbp.biosample_accession) as total_biosamples,
    COUNT(DISTINCT CASE WHEN bwa.accession IS NOT NULL THEN sbp.biosample_accession END) as biosamples_with_attributes,
    COUNT(DISTINCT CASE WHEN sb.accession IS NOT NULL THEN sbp.biosample_accession END) as satisfying_biosamples
  FROM sra_biosamples_bioprojects sbp
  LEFT JOIN biosamples_with_attributes bwa ON sbp.biosample_accession = bwa.accession
  LEFT JOIN satisfying_biosamples sb ON sbp.biosample_accession = sb.accession
  WHERE sbp.bioproject_accession IS NOT NULL
    AND bwa.accession IS NOT NULL
  GROUP BY sbp.bioproject_accession
)
SELECT
  bp.accession as bioproject_accession,
  bp.name as bioproject_name,
  bp.title as bioproject_title,
  bp.organism_name,
  bp.data_type,
  bp.method_type,
  bp.sample_scope,
  bp.release_date,
  bc.total_biosamples,
  bc.biosamples_with_attributes,
  bc.satisfying_biosamples,
  ROUND(100.0 * bc.satisfying_biosamples / NULLIF(bc.biosamples_with_attributes, 0), 2) as pct_satisfying
FROM bioproject_counts bc
LEFT JOIN bioprojects_flattened bp ON bc.bioproject_accession = bp.accession
ORDER BY bc.satisfying_biosamples DESC, bc.biosamples_with_attributes DESC;
