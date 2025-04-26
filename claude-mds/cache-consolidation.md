# Cache Consolidation Documentation

## Consolidated Cache File

A consolidated cache file has been created that combines all existing requests-cache files into a single file:

- **File name**: `external-metadata-awareness-requests-cache.sqlite`
- **Location**: Repository root directory
- **Size**: 2.1 GB
- **Creation date**: April 1, 2025
- **Contents**: Combined data from:
  - `requests_cache.sqlite` (816 MB)
  - `new_env_triad_values_splitter_cache.sqlite` (3.6 MB)
  - `my_cache.sqlite` (3.6 MB)
  - `notebooks/studies_exploration/ncbi_annotation_mining/requests_cache.sqlite` (1.4 GB)

## Statistics

- **Total responses**: 299,778
- **Total redirects**: 143,546
- **Unique responses**: All duplicate entries have been eliminated

## How to Use the Consolidated Cache

To use this consolidated cache file in your scripts, modify the cache installation line:

```python
# Original individual cache files
requests_cache.install_cache("requests_cache", expire_after=datetime.timedelta(days=30))

# To use the consolidated cache instead:
requests_cache.install_cache("external-metadata-awareness-requests-cache", expire_after=datetime.timedelta(days=30))
```

## Migration Plan

### Immediate Actions
- ✅ Create consolidated cache file
- ✅ Document the consolidation process
- ❌ Update application code to use the consolidated cache

### Future Steps
1. Modify all scripts to use the consolidated cache:
   ```python
   # Add this line to the top of each file
   import datetime
   
   # Replace existing cache installation with:
   requests_cache.install_cache("external-metadata-awareness-requests-cache", expire_after=datetime.timedelta(days=30))
   ```

2. Remove old cache files after the transition is verified:
   - `requests_cache.sqlite`
   - `new_env_triad_values_splitter_cache.sqlite`
   - `my_cache.sqlite`
   - `notebooks/studies_exploration/ncbi_annotation_mining/requests_cache.sqlite`

3. Update `requests-caching.md` to reference the consolidated cache

## Implementation Script

The consolidation was performed using the `combine_cache_files.py` script, which:
1. Creates a new empty cache database with the correct schema
2. Iterates through each source cache file
3. Imports all entries, ignoring duplicates
4. Preserves original cache files

This approach ensures a non-destructive migration path, allowing validation before switching to the new cache.