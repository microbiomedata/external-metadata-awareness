Working space for wrangling gene to disease sources into a single table

## Data Sources
  
* OMIM & Orphanet via Exomiser pipeline
* The GenCC directly loaded from GenCC downloads

## Process

1. Load each source into its own table in duckdb
2. Create DDL to define the merged destination table
3. Copy each source from its table to the destination table
4. Export to tsv, parquet, duckdb 
5. Upload to monarch gcp bucket as a date named release YYYY-MM-DD



