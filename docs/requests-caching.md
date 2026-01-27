# Requests Caching in External Metadata Awareness

This document lists all places where requests caches are used in the codebase:

1. **new_env_triad_ols_annotator.py**
   - Cache name: `"requests_cache"`
   - Expiration time: 30 days
   - Line 26: `requests_cache.install_cache("requests_cache", expire_after=datetime.timedelta(days=30))`

2. **new_bioportal_curie_mapper.py**
   - Cache name: `"requests_cache"`
   - Expiration time: 30 days
   - Line 19: `requests_cache.install_cache("requests_cache", expire_after=datetime.timedelta(days=30))`

3. **new_env_triad_values_splitter.py**
   - Cache name: `"new_env_triad_values_splitter_cache"`
   - Expiration time: 30 days
   - Line 237: `requests_cache.install_cache('new_env_triad_values_splitter_cache', expire_after=datetime.timedelta(days=30))`

4. **build_and_apply_lexical_index_from_env_triad_values_ner.ipynb**
   - Cache name: `"requests_cache"`
   - Expiration time: 30 days
   - Cell 9: `requests_cache.install_cache(requests_cache_name, expire_after=requests_cache_expire_after)`
   - The variable `requests_cache_name` is set to `"requests_cache"` and `requests_cache_expire_after` is set to `datetime.timedelta(days=30)`

> Note: All cache periods have been standardized to 30 days using the `datetime.timedelta` approach for consistency.
> The notebook file **new_env_triad_values_splitter.ipynb** mentioned previously was not found in the repository.