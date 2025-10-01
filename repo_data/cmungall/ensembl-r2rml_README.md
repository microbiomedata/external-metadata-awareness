# Experimental R2RML mapping for Ensembl RDF using Ensembl SQL DB

## ONTOP Setup

Download [ontop](https://ontop-vkg.org/) add the [mysql](https://mvnrepository.com/artifact/mysql/mysql-connector-java) or [mariadb](https://mariadb.com/kb/en/about-mariadb-connector-j/) jdbc driver to the jdbc directory of your ontop installation.

## RDF Model

The RDF model attempts to be as it was when the RDF was last dumped (Ensembl release 102).
With all the pro's and con's of that.

## Ontop

Gather metadata, this is very slow and needs a very large connection timeout to work!

```
ontop extract-db-metadata -p ensembl_aconthochromis_polyacantus_core_107_1.properties -o ensembl_aconthochromis_polyacantus_core_107_1.metadata
```

## Query

While developing

```


```


## Help wanted

This is just a quick start and not complete. Patches and example queries are very welcome.

