1. Primary MongoDB Import Scripts:
  - notebooks/studies_exploration/simons_wishlist/filtered_sra_metadata_to_mongo.ipynb: Directly queries BigQuery's nih-sra-datastore.sra.metadata table and writes results to MongoDB collection
ncbi_metadata.filtered_sra_metadata. This notebook uses complex filtering to find records with environmental context triads.
2. Parquet Pipeline:
  - external_metadata_awareness/sra_parquet_to_mongodb.py: Imports SRA data from Parquet files into MongoDB. This suggests you may have used a two-step process: BigQuery → Parquet → MongoDB in some
workflows.
3. TSV Export/Import Pipeline:
  - external_metadata_awareness/export_sra_accession_pairs.py: Reads from BigQuery's nih-sra-datastore.sra.metadata but exports to TSV files rather than directly to MongoDB.
  - external_metadata_awareness/sra_accession_pairs_tsv_to_mongo.py: Likely the second step in this pipeline to load TSV into MongoDB.

  Based on CLAUDE.md, it appears the BigQuery data was stored in several MongoDB collections:
- ncbi_metadata.filtered_sra_metadata (~2.7M documents)
- biosamples.sra_metadata (~35M documents)
- ncbi_metadata.sra_metadata (in the loadbalancer instance)
