# Requests Caching in External Metadata Awareness

This document lists all places where requests caches are used in the codebase:

1. **new_env_triad_ols_annotator.py**
   - Cache name: `"requests_cache"`
   - Expiration time: 6,048,000 seconds (70 days)
   - Line 25: `requests_cache.install_cache("requests_cache", expire_after=6048000)`

2. **new_bioportal_curie_mapper.py**
   - Cache name: `"requests_cache"`
   - Expiration time: 6,048,000 seconds (70 days)
   - Line 16: `requests_cache.install_cache("requests_cache", expire_after=6048000)`

3. **new_env_triad_values_splitter.py**
   - Cache name: `"new_env_triad_values_splitter_cache"`
   - Expiration time: 3,600 seconds (1 hour)
   - Line 247: `requests_cache.install_cache('new_env_triad_values_splitter_cache', expire_after=3600)`

4. **new_env_triad_values_splitter.ipynb**
   - Cache name: `"my_cache"`
   - Expiration time: 3,600 seconds (1 hour)
   - Cell 27: `requests_cache.install_cache('my_cache', expire_after=3600)`

5. **build_and_apply_lexical_index_from_env_triad_values_ner.py**
   - Cache name: `"requests_cache"`
   - Expiration time: 6,048,000 seconds (70 days)
   - Line 88: `requests_cache.install_cache(requests_cache_name, expire_after=requests_cache_expire_after)`
   - The variable `requests_cache_name` is set to `"requests_cache"` and `requests_cache_expire_after` is set to `6048000`

6. **build_and_apply_lexical_index_from_env_triad_values_ner.ipynb**
   - Cache name: `"requests_cache"`
   - Expiration time: 6,048,000 seconds (70 days)
   - Cell 9: `requests_cache.install_cache(requests_cache_name, expire_after=requests_cache_expire_after)`
   - The variable `requests_cache_name` is set to `"requests_cache"` and `requests_cache_expire_after` is set to `6048000`