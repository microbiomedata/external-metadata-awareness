## Mondo Translator subset

As a subset curator, you only ever edit translator-excluded.sparql (to curate the automatic exclusion rules) or exclusion-list-manual.txt to exclude individual classes from the Mondo Translator subset.

Once both files are in the desired state, run:


```
make mondo-translator.owl -B
```

The -B ensures that a new version of Mondo is downloaded. You can omit the -B if you want to use the version you have previously downloaded.