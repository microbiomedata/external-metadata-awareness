# MongoDB Measurement Discovery Pipeline - Session Addendum 2025-09-27

## Overview
This session focused on completing the NCBI metadata measurement discovery pipeline and creating baseline counting functionality for harmonized field usage analysis. We successfully implemented a robust three-step counting system for biosamples and bioprojects per harmonized_name, with proper error handling and recovery mechanisms.

## What We're Trying to Accomplish

### Primary Goals
1. **Baseline Counting**: Count unique biosamples and bioprojects per harmonized_name to prioritize measurement field analysis
2. **Memory-Efficient Processing**: Handle 52M+ biosample attributes and 31M+ SRA relationships without hitting MongoDB's 16MB document limits
3. **Robust Pipeline**: Create makefile-based workflow with proper indexing, error handling, and recovery capabilities
4. **Data Integration**: Combine NCBI biosample data with SRA bioproject relationships for comprehensive analysis

### Secondary Goals
- Prepare foundation for Method 1 (unit assertions) and Method 2 (mixed content) measurement discovery
- Create reusable patterns for large-scale MongoDB aggregations
- Establish checkpoint-based processing for long-running operations

## What We Implemented

### 1. SRA Biosample-Bioproject Relationship Pipeline
```bash
# Extract relationships from SRA parquet files using DuckDB
make -f Makefiles/sra_metadata.Makefile local/sra_biosample_bioproject_pairs.tsv

# Load into MongoDB with configurable column names  
make -f Makefiles/sra_metadata.Makefile load-sra-pairs-to-mongo

# Create performance indexes
make -f Makefiles/sra_metadata.Makefile index-sra-pairs
```

**Key Files:**
- `sql/extract_sra_biosample_bioproject_pairs_to_tsv.sql` - DuckDB extraction query
- `external_metadata_awareness/sra_accession_pairs_tsv_to_mongo.py` - Flexible TSV loader with click options
- Updated `pyproject.toml` script aliases

**Results:** 31,809,492 unique biosample-bioproject pairs loaded successfully

### 2. Three-Step Harmonized Name Counting System
```bash
# Individual steps for debugging/recovery
make -f Makefiles/measurement_discovery.Makefile count-biosamples-step1
make -f Makefiles/measurement_discovery.Makefile count-bioprojects-step2  
make -f Makefiles/measurement_discovery.Makefile merge-counts-step3

# Combined pipeline
make -f Makefiles/measurement_discovery.Makefile count-biosamples-and-bioprojects-per-harmonized-name
```

**Architecture:**
- **Step 1**: Count unique biosamples per harmonized_name → `temp_biosample_counts` (695 results)
- **Step 2**: Count unique bioprojects per harmonized_name via $lookup → `temp_bioproject_counts` (671 results)  
- **Step 3**: Merge results → `harmonized_name_usage_stats` → cleanup temps

**Key Features:**
- Strategic index creation at optimal times
- Graceful handling of existing indexes with try/catch
- Memory-efficient approach using temporary collections
- Built-in cleanup and progress reporting

## What We Struggled With

### 1. Memory Explosions in MongoDB Aggregations
**Problem:** Repeated "Used too much memory for a single array" errors when using `$addToSet` with millions of values

**Root Cause:** Original approach tried to store all content values in arrays, hitting MongoDB's 16MB document limit

**Solution:** Switched to two-stage approach using temporary collections instead of in-memory arrays

### 2. Network Timeouts with Lid-Closed MacBook
**Problem:** Long-running aggregations failed when MacBook went to sleep or had network interruptions

**Root Cause:** MongoDB connection timeouts during multi-hour operations

**Solution:** 
- Broke monolithic operations into smaller, recoverable steps
- Used makefile targets for each checkpoint
- Designed resumable pipeline that can continue from intermediate results

### 3. Index Conflicts During Aggregation
**Problem:** "Index already exists with a different name" and "indexes of target collection changed during processing" errors

**Root Causes:**
- Trying to create indexes with same field spec but different names
- Creating indexes on target collections during $out operations

**Solutions:**
- Wrapped index creation in try/catch blocks for graceful handling
- Created all necessary indexes **before** starting aggregations, not during
- Used `{background: true}` for non-blocking index creation

### 4. Complex $lookup Performance Issues
**Problem:** Step 2 aggregation was extremely slow without proper indexing

**Root Cause:** $lookup join against 31M+ documents without index on foreign key

**Solution:** Created `sra_biosamples_bioprojects.biosample_accession` index before Step 2

## Alternative Approaches That Work

### 1. DuckDB for Large Data Extraction
**Instead of:** Complex MongoDB aggregations on raw data
**Use:** DuckDB CLI with SQL for initial data extraction from parquet files
```sql
CREATE OR REPLACE TABLE sra_biosamples_bioprojects AS
SELECT DISTINCT biosample, bioproject 
FROM read_parquet('local/sra_metadata_parquet/*')
WHERE biosample IS NOT NULL AND bioproject IS NOT NULL;
```

**Benefits:** 
- Much faster for analytical queries on large datasets
- Better memory management for complex joins
- Familiar SQL syntax for data extraction

### 2. Checkpoint-Based Processing
**Instead of:** Monolithic scripts that restart from beginning on failure
**Use:** Multiple makefile targets with intermediate collections
```make
step1: temp_collection_1
step2: temp_collection_2  
step3: final_result
combined: step1 step2 step3
```

**Benefits:**
- Can resume from any failed step
- Easier debugging of individual components
- Better progress visibility

### 3. Graceful Index Handling
**Instead of:** Assuming indexes don't exist
**Use:** Try/catch wrapper for all index creation
```javascript
try { 
    db.collection.createIndex({field: 1}, {background: true}); 
} catch(e) { 
    print('Index exists: ' + e.message); 
}
```

**Benefits:**
- Idempotent operations (can run multiple times safely)
- Better error messages for debugging
- Continues processing even with index conflicts

## Key Lessons Learned

### 1. Memory Management is Critical
- MongoDB's 16MB document limit applies to intermediate aggregation results
- Use temporary collections instead of large in-memory arrays
- Monitor aggregation memory usage with `allowDiskUse: true`

### 2. Strategic Indexing Timing Matters
- Create indexes **before** heavy operations, not during
- Use `{background: true}` for non-blocking creation
- Index foreign key fields before $lookup operations

### 3. Recovery Mechanisms Are Essential
- Design workflows that can resume from checkpoints
- Use intermediate collections as restart points
- Separate complex operations into smaller, testable units

### 4. Network Reliability Cannot Be Assumed
- Long-running operations will encounter network issues
- Build resumability into workflows from the start
- Consider using `caffeinate` for overnight operations

## Current Status

### Completed Successfully
- ✅ SRA biosample-bioproject relationship data loaded (31.8M pairs)
- ✅ Proper indexes created for performance  
- ✅ Baseline counting system operational (695 biosample counts, 671 bioproject counts)
- ✅ Final `harmonized_name_usage_stats` collection created
- ✅ Robust three-step makefile workflow with recovery

### Ready for Next Phase
- 🚀 Method 1: Unit assertions counting script
- 🚀 Method 2: Mixed content (letters + numbers) counting script  
- 🚀 Integration with existing measurement discovery pipeline

## Code Quality Improvements Made

### 1. Configurable Column Names
Added click options to TSV loader for flexibility:
```python
@click.option("--biosample-column", default="biosample", help="Name of biosample column in TSV")
@click.option("--bioproject-column", default="bioproject", help="Name of bioproject column in TSV")
```

### 2. Proper Error Handling
All index creation now uses graceful error handling:
```javascript
try { db.collection.createIndex(...); } catch(e) { print('Handled: ' + e.message); }
```

### 3. Progress Reporting
All steps include timestamp logging and progress updates:
```javascript
print('[' + new Date().toISOString() + '] Step description');
```

### 4. Resource Cleanup
Automatic cleanup of temporary collections after successful completion:
```javascript
db.temp_biosample_counts.drop();
db.temp_bioproject_counts.drop();
```

## Future Optimization Opportunities

1. **Parallel Processing**: Could run biosample and bioproject counting in parallel
2. **Incremental Updates**: Design for updating counts when new data arrives
3. **Compressed Indexes**: Use sparse indexes for optional fields
4. **Connection Pooling**: Implement connection retry logic for long operations

This three-step approach provides a solid foundation for the remaining measurement discovery work while addressing all the memory, networking, and indexing challenges we encountered.