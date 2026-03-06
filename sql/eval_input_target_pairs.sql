-- Extract eval input-target pairs from the submissions DuckDB.
--
-- Input columns (what the user/study provides):
--   study_name, description, notes
--
-- Target columns (what an LLM should predict):
--   env_broad_scale, env_local_scale, env_medium, ecosystem hierarchy, etc.
--
-- Usage:
--   duckdb local/nmdc_submissions.duckdb < sql/eval_input_target_pairs.sql
--
-- Or from Python:
--   conn = duckdb.connect("local/nmdc_submissions.duckdb", read_only=True)
--   df = conn.execute(open("sql/eval_input_target_pairs.sql").read()).fetchdf()

SELECT
    s.study_name,
    s.description,
    s.notes,
    b.sampleData,
    b.env_broad_scale,
    b.env_local_scale,
    b.env_medium,
    b.geo_loc_name,
    b.depth,
    b.ecosystem,
    b.ecosystem_type,
    b.ecosystem_subtype,
    b.ecosystem_category,
    b.specific_ecosystem,
    b.analysis_type
FROM nmdc_submissions s
JOIN flattened_submission_biosamples b
    ON s.submission_id = b.submission_id
WHERE b.status = 'Released'
