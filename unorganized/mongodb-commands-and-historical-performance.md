```shell
make load-biosamples-into-mongo
```

> 2024-08-13T19:00:28.052828: 40000, 0.1%
> 2024-08-13T19:00:57.346565: 80000, 0.2%
> 2024-08-13T19:01:34.743793: 120000, 0.3%
>
>2024-08-14T05:34:00.487742: 43104782, 107.8%
>
>Process finished with exit code 0

```shell
mongosh
```

```mongo
use biosamples

db.biosamples.estimatedDocumentCount()

biosamples> db.biosamples.countDocuments({})
```

> 40347716

```shell
grep -c "</BioSample>" local/biosample_set.xml
```

> 40347716

Ids have been saved as strings. There are probably some Booleans in there too that are expressed as integers as a
strings

```mongo
db.biosamples.createIndex({ accession: 1 })

db.collectionName.createIndex({ "Package.value": 1 })
```

```compass
{"Package.value": "MIMS.me.soil.6.0"}
```
