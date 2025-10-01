# Working with NCBI SRA Metadata in DuckDB

## Recommended Default: Query Parquet In Place
- **Zero copy/ingest time**: No need to import or duplicate data.
- **Interoperability**: Keeps data usable by Spark, Polars, Arrow, pandas, etc.
- **Performance**: DuckDB can push down filters, prune columns, and exploit Parquet statistics and partitioning.

### How To
```sql
-- open or create a small catalog
duckdb sra.duckdb

LOAD httpfs;            -- needed if files are on GCS/S3
PRAGMA threads=auto;

-- Point at directory of files
CREATE VIEW sra AS
SELECT * FROM read_parquet('data/sra/*.parquet');

-- Queries
SELECT study_accession, count(*) 
FROM sra 
WHERE collection_date >= DATE '2020-01-01'
GROUP BY 1 
ORDER BY 2 DESC;
```

**Tips**
- Files should be moderately sized (128–512 MB).
- Coalesce tiny files if needed.
- Use `EXPLAIN` to verify predicate and column pushdown.

---

## When To Materialize Into `.duckdb`
Do this if:
1. You need to **mutate data** (INSERT/UPDATE/DELETE).
   ```sql
   CREATE TABLE sra_native AS SELECT * FROM read_parquet('data/sra/*.parquet');
   ```

2. You want a **portable, single-file artifact** to share.

3. You need **performance tuning for repeated workloads** (ANALYZE, stats).

4. You want **MotherDuck sync or database-level features**.

---

## Hybrid Pattern (Often Best)
- Keep raw SRA as Parquet.
- Maintain a lightweight `.duckdb` catalog with:
  - Views over Parquet
  - Small materialized tables for frequent joins or updates
  - Macros/UDFs, virtual schemas

---

## Practical Checklist
- Coalesce many small Parquet files:
  ```sql
  COPY (SELECT * FROM read_parquet('data/sra/*.parquet'))
  TO 'data/sra_coalesced/*.parquet' (FORMAT PARQUET, ROW_GROUP_SIZE=12800000);
  ```

- Store common projections:
  ```sql
  CREATE TABLE sra_min AS
  SELECT run_accession, study_accession, sample_accession, platform, instrument_model, collection_date
  FROM sra;
  ```

- Pin your catalog/views in `sra.duckdb` for reproducibility.

---

## Bottom Line
Keep SRA in **Parquet** and query directly.  
Add a `.duckdb` file for your **catalog** (views, macros) and any **materialized subsets** you need often.  
Convert everything only if your workflow truly benefits from a single-file database with in-place updates.
