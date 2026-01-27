-- create_legacy_views.sql
-- Creates views matching the old DuckDB schema expected by generate_voting_sheet.ipynb
--
-- The voting sheet notebook expects 'attributes' and 'links' tables with specific columns.
-- This script creates views on top of the new flattened schema to provide backwards compatibility.
--
-- Usage:
--   duckdb <database.duckdb> < sql/create_legacy_views.sql
--
-- Or via Makefile:
--   make -f Makefiles/ncbi_to_duckdb.Makefile create-legacy-views

-- Create 'attributes' view matching old schema
-- Old schema expected columns: id, content, harmonized_name, package_content
CREATE OR REPLACE VIEW attributes AS
SELECT
    a.accession AS id,
    a.content,
    a.harmonized_name,
    b.package_content
FROM biosamples_attributes a
LEFT JOIN biosamples_flattened b ON a.accession = b.accession;

-- Create 'links' view matching old schema
-- Old schema expected columns: id, content, target
CREATE OR REPLACE VIEW links AS
SELECT
    accession AS id,
    content,
    target
FROM biosamples_links;

-- Verify views created successfully
SELECT 'attributes' as view_name, COUNT(*) as rows FROM attributes
UNION ALL
SELECT 'links' as view_name, COUNT(*) as rows FROM links;
