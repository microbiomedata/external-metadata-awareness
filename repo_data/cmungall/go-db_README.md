# go-db

go-db is a Python package that provides a convenient way to load Gene Ontology (GO) annotations from GAF files into a DuckDB database for efficient querying and analysis. It includes scripts for loading data, validating the loaded data against GO rules, and running common queries.


## Usage

Currently you must have the repo checked out and be in the root directory.

```
poetry install
poetry run go-db --help
```

To see all options:

```
poetry run go-db --help
```

You must also place a copy of `go.db` in the `db` directory.

## Loading from GAF

Given `data/mgi.gaf` as input:

```
poetry run go-db load -d db/mgi.db data/mgi.gaf
```

Note that the (very smart) duckdb auto-CSV detector seems to do the right thing with GAFs
but this should be fully validated.

__NOTE__: gaf2 and 17 columns is assumed

The loader is very simple - it just wraps [src/go_db/gaf.ddl.sql](src/go_db/gaf.ddl.sql)

This has two tables:

1. A "flat" table that is a denormalized representation (no parsing)
2. The normalized table where `|` separators are split into duckdb lists

The loader is basically a wrapper like a Makefile

## Validation

This is done automatically after loading, unless `--no-validate` is passed

It can also be run at any time with:

```
poetry run go-db validate -d mgi.db
```

This is just a simple wrapper for the SQL views here:

[src/go_db/go_rules.sql](src/go_db/go_rules.sql)

Only a handful are defined. These have not been checked
(I made them by giving claude the schema and a PDF of the go rules documentation)

## Closure queries

Attach a semsql build of GO (currently sqlite)

```
attach 'db/go.semsql.db';
```



## Benchmarking

This is currently incomplete but to give a sense, to load a 6G (compressed) GAF:

```
tome poetry run go-db -load -d gcrp.db goa_uniprot_gcrp.gaf.gz 
2197.27s user 110.23s system 664% cpu 5:47.33 total
```

This is half a billion associations:

```
D select count(*) from gaf_association;
┌──────────────┐
│ count_star() │
│    int64     │
├──────────────┤
│    419521545 │
└──────────────┘
```

24k species:

```
D select count(DISTINCT db_object_taxon) from gaf_association;
┌─────────────────────────────────┐
│ count(DISTINCT db_object_taxon) │
│              int64              │
├─────────────────────────────────┤
│                           24196 │
└─────────────────────────────────┘
```

Note also that queries are fast, including closure queries; e.g annotations to descendants of nucleus:

```
D select count(*) from gaf_association as a, go.entailed_edge as e where ontology_class_ref=e.subject and e.object='GO:0005634';
┌──────────────┐
│ count_star() │
│    int64     │
├──────────────┤
│     41502387 │
└──────────────┘
```

Grouping queries are also fast

```
D select db_object_taxon, count(*) as n from gaf_association where evidence_type != 'IEA' group by all having n > 1000;
┌─────────────────┬────────┐
│ db_object_taxon │   n    │
│     varchar     │ int64  │
├─────────────────┼────────┤
│ taxon:284593    │   4682 │
│ taxon:2711      │  26982 │
│ taxon:3983      │  37494 │
│ taxon:29655     │  25902 │
│ taxon:3641      │  30616 │
│ taxon:6238      │  28824 │
│ taxon:10116     │ 339989 │
│ taxon:515635    │   1857 │
│ taxon:105231    │  15644 │
│ taxon:9031      │  28416 │
│ taxon:330879    │  27064 │
│ taxon:5786      │  16380 │
│ taxon:227321    │  28418 │
│ taxon:10228     │  21717 │
│ taxon:418459    │  15857 │
│ taxon:6239      │  58538 │
│ taxon:64091     │   1635 │
│ taxon:1392      │   4523 │
│ taxon:243274    │   2104 │
│ taxon:9646      │   1169 │
│     ·           │     ·  │
│     ·           │     ·  │
│     ·           │     ·  │
│ taxon:9913      │  93347 │
│ taxon:665079    │  15615 │
│ taxon:4097      │  71322 │
│ taxon:5888      │  45377 │
│ taxon:4558      │  36859 │
│ taxon:81824     │  15543 │
│ taxon:412133    │  28519 │
│ taxon:9823      │  50408 │
│ taxon:3702      │ 105487 │
│ taxon:4432      │  31943 │
│ taxon:9258      │  49353 │
│ taxon:3880      │  42008 │
│ taxon:15368     │  34756 │
│ taxon:294381    │  11247 │
│ taxon:10036     │   1262 │
│ taxon:188937    │   2578 │
│ taxon:436308    │   1340 │
│ taxon:184922    │   5977 │
│ taxon:289376    │   1992 │
│ taxon:10141     │   1818 │
├─────────────────┴────────┤
│   160 rows (40 shown)    │
└──────────────────────────┘
```

This takes a few seconds:

```
select * from GORULE_0000005_violations limit 100;
100% ▕████████████████████████████████████████████████████████████▏
┌───────────┬──────────┬───────────────────┬────────────┬────────────────────┬──────────────────────┬───┬──────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│    db     │ local_id │ db_object_symbol  │ qualifiers │ ontology_class_ref │ supporting_referen…  │ … │     subject      │  with_or_from_list   │ supporting_referen…  │ db_object_synonyms…  │ annotation_extensi…  │
│  varchar  │ varchar  │      varchar      │  varchar   │      varchar       │       varchar        │   │     varchar      │      varchar[]       │      varchar[]       │      varchar[]       │      varchar[]       │
├───────────┼──────────┼───────────────────┼────────────┼────────────────────┼──────────────────────┼───┼──────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ UniProtKB │ E1BNK3   │ TGFB1             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:E1BNK3 │ [UniProtKB:P01137]   │ [GO_REF:0000024]     │ [TGFB1]              │                      │
│ UniProtKB │ Q5RCV3   │ NBN               │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q5RCV3 │ [UniProtKB:O60934]   │ [GO_REF:0000024]     │ [NBN]                │                      │
│ UniProtKB │ F7HFK5   │ PPIB              │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:F7HFK5 │ [UniProtKB:P24367]   │ [GO_REF:0000024]     │ [PPIB]               │                      │
│ UniProtKB │ Q6XV80   │ nbn.L             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q6XV80 │ [UniProtKB:O60934]   │ [GO_REF:0000024]     │ [nbn.L, NBS1, nbn,…  │                      │
│ UniProtKB │ G3TLB6   │ PPIB              │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:G3TLB6 │ [UniProtKB:P24367]   │ [GO_REF:0000024]     │ [PPIB]               │                      │
│ UniProtKB │ Q9Y366   │ IFT52             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q9Y366 │ [UniProtKB:Q946G4]   │ [GO_REF:0000024]     │ [IFT52, C20orf9, N…  │                      │
│ UniProtKB │ F7BZB1   │ PPIB              │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:F7BZB1 │ [UniProtKB:P24367]   │ [GO_REF:0000024]     │ [PPIB]               │                      │
│ UniProtKB │ G1L6S5   │ CRTAP             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:G1L6S5 │ [UniProtKB:Q90830]   │ [GO_REF:0000024]     │ [CRTAP]              │                      │
│ UniProtKB │ A6QLJ0   │ ERCC2             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:A6QLJ0 │ [UniProtKB:P18074]   │ [GO_REF:0000024]     │ [ERCC2]              │                      │
│ UniProtKB │ P02548   │ NEFL              │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:P02548 │ [UniProtKB:P07196]   │ [GO_REF:0000024]     │ [NEFL]               │                      │
│ UniProtKB │ Q5ZIK2   │ PDZD11            │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q5ZIK2 │ [UniProtKB:Q5EBL8-1] │ [GO_REF:0000024]     │ [PDZD11, PDZK11, R…  │                      │
│ UniProtKB │ P97494   │ Gclc              │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:P97494 │ [UniProtKB:P48506]   │ [GO_REF:0000024]     │ [Gclc, Glclc]        │                      │
│ UniProtKB │ G1RTT5   │ TGFB1             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:G1RTT5 │ [UniProtKB:P01137]   │ [GO_REF:0000024]     │ [TGFB1]              │                      │
│ UniProtKB │ Q6DIA9   │ Fbxo27            │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q6DIA9 │ [UniProtKB:Q8NI29]   │ [GO_REF:0000024]     │ [Fbxo27]             │                      │
│ UniProtKB │ Q1LZ75   │ ERCC1             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q1LZ75 │ [UniProtKB:P07992]   │ [GO_REF:0000024]     │ [ERCC1]              │                      │
│ UniProtKB │ L5KRZ8   │ PAL_GLEAN10000575 │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:L5KRZ8 │ [UniProtKB:P01137]   │ [GO_REF:0000024]     │ [PAL_GLEAN10000575]  │                      │
│ UniProtKB │ Q811D0   │ Dlg1              │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q811D0 │ [UniProtKB:Q12959]   │ [GO_REF:0000024]     │ [Dlg1, Dlgh1]        │                      │
│ UniProtKB │ Q28IT1   │ erlec1            │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q28IT1 │ [UniProtKB:Q96DZ1]   │ [GO_REF:0000024]     │ [erlec1, TNeu121c1…  │                      │
│ UniProtKB │ Q60HG1   │ ERCC3             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q60HG1 │ [UniProtKB:P19447]   │ [GO_REF:0000024]     │ [ERCC3, QnpA-11695]  │                      │
│ UniProtKB │ Q2YDW7   │ Kmt5a             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q2YDW7 │ [UniProtKB:Q9NQR1]   │ [GO_REF:0000024]     │ [Kmt5a, Setd8]       │                      │
│     ·     │   ·      │   ·               │    ·       │     ·              │       ·              │ · │        ·         │         ·            │        ·             │       ·              │          ·           │
│     ·     │   ·      │   ·               │    ·       │     ·              │       ·              │ · │        ·         │         ·            │        ·             │       ·              │          ·           │
│     ·     │   ·      │   ·               │    ·       │     ·              │       ·              │ · │        ·         │         ·            │        ·             │       ·              │          ·           │
│ UniProtKB │ Q9H2M9   │ RAB3GAP2          │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q9H2M9 │ [UniProtKB:Q5U1Z0]   │ [GO_REF:0000024]     │ [RAB3GAP2, KIAA0839] │                      │
│ UniProtKB │ Q62108   │ Dlg4              │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q62108 │ [UniProtKB:P31016]   │ [GO_REF:0000024]     │ [Dlg4, Dlgh4, Psd95] │                      │
│ UniProtKB │ P11942   │ Cd3g              │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:P11942 │ [UniProtKB:P09693]   │ [GO_REF:0000024]     │ [Cd3g]               │                      │
│ UniProtKB │ P68399   │ CSNK2A1           │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:P68399 │ [UniProtKB:P68400]   │ [GO_REF:0000024]     │ [CSNK2A1, CK2A1]     │                      │
│ UniProtKB │ M3W421   │ TGFB1             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:M3W421 │ [UniProtKB:P01137]   │ [GO_REF:0000024]     │ [TGFB1]              │                      │
│ UniProtKB │ Q3SX24   │ FBXO6             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q3SX24 │ [UniProtKB:Q9QZN4]   │ [GO_REF:0000024]     │ [FBXO6, FBS2, FBX6]  │                      │
│ UniProtKB │ P18341   │ TGFB1             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:P18341 │ [UniProtKB:P01137]   │ [GO_REF:0000024]     │ [TGFB1]              │                      │
│ UniProtKB │ Q8K2C7   │ Os9               │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q8K2C7 │ [UniProtKB:Q13438]   │ [GO_REF:0000024]     │ [Os9]                │                      │
│ UniProtKB │ C0H5E1   │ PF3D7_1326800     │ enables    │ GO:0005515         │ PMID:19103232        │ … │ UniProtKB:C0H5E1 │                      │ [PMID:19103232]      │ [PF3D7_1326800]      │                      │
│ UniProtKB │ I3N2Y6   │ CRTAP             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:I3N2Y6 │ [UniProtKB:Q90830]   │ [GO_REF:0000024]     │ [CRTAP]              │                      │
│ UniProtKB │ Q6NXB2   │ pdzd11            │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q6NXB2 │ [UniProtKB:Q5EBL8-1] │ [GO_REF:0000024]     │ [pdzd11, pdzk11, z…  │                      │
│ UniProtKB │ P50414   │ TGFB1             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:P50414 │ [UniProtKB:P01137]   │ [GO_REF:0000024]     │ [TGFB1]              │                      │
│ UniProtKB │ Q62696   │ Dlg1              │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q62696 │ [UniProtKB:Q12959]   │ [GO_REF:0000024]     │ [Dlg1, Dlgh1]        │                      │
│ UniProtKB │ Q17QJ6   │ BCL10             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q17QJ6 │ [UniProtKB:O95999]   │ [GO_REF:0000024]     │ [BCL10]              │                      │
│ UniProtKB │ Q17QJ6   │ BCL10             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q17QJ6 │ [UniProtKB:O95999]   │ [GO_REF:0000024]     │ [BCL10]              │ [part_of(GO:003166…  │
│ UniProtKB │ Q9N0C8   │ FBXO27            │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q9N0C8 │ [UniProtKB:Q8NI29]   │ [GO_REF:0000024]     │ [FBXO27, QccE-12959] │                      │
│ UniProtKB │ Q9DE07   │ NBN               │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q9DE07 │ [UniProtKB:O60934]   │ [GO_REF:0000024]     │ [NBN, NBS1]          │                      │
│ UniProtKB │ Q2YDJ8   │ KMT5A             │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:Q2YDJ8 │ [UniProtKB:Q9NQR1]   │ [GO_REF:0000024]     │ [KMT5A, SETD8]       │                      │
│ UniProtKB │ S9YCI6   │ PPIB              │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:S9YCI6 │ [UniProtKB:P24367]   │ [GO_REF:0000024]     │ [PPIB, CB1_0007150…  │                      │
│ UniProtKB │ D2GYR4   │ PPIB              │ enables    │ GO:0005515         │ GO_REF:0000024       │ … │ UniProtKB:D2GYR4 │ [UniProtKB:P24367]   │ [GO_REF:0000024]     │ [PPIB, PANDA_002160] │                      │
├───────────┴──────────┴───────────────────┴────────────┴────────────────────┴──────────────────────┴───┴──────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤
│ 100 rows (40 shown)                                                                                                                                                                            22 columns (11 shown) │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

```

# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [monarch-project-template](https://github.com/monarch-initiative/monarch-project-template) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).
