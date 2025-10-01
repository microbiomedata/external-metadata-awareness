# Monarch Semantic Similarity Profiles
- **Profiles Directory**: `profiles`

## Ontologies used


### PHENIO-FLAT

- **ID**: `phenio-flat`


### PHENIO-RELEASE

- **ID**: `phenio-release`
- **Mirror From**: [https://github.com/monarch-initiative/phenio/releases/latest/download/phenio.owl.gz](https://github.com/monarch-initiative/phenio/releases/latest/download/phenio.owl.gz)


### PHENIO-EQUIVALENT

- **ID**: `phenio-equivalent`


### PHENIO-MONARCH

- **ID**: `phenio-monarch`


### UPHENO1

- **ID**: `upheno1`
- **Mirror From**: [https://raw.githubusercontent.com/obophenotype/upheno/refs/heads/master/upheno.owl](https://raw.githubusercontent.com/obophenotype/upheno/refs/heads/master/upheno.owl)


### HP

- **ID**: `hp`
- **Mirror From**: [http://purl.obolibrary.org/obo/hp.owl](http://purl.obolibrary.org/obo/hp.owl)

- **Root term**: `HP:0000118`


### MP

- **ID**: `mp`
- **Mirror From**: [http://purl.obolibrary.org/obo/mp.owl](http://purl.obolibrary.org/obo/mp.owl)

- **Root term**: `MP:0000001`


### ZP

- **ID**: `zp`
- **Mirror From**: [http://purl.obolibrary.org/obo/zp.owl](http://purl.obolibrary.org/obo/zp.owl)

- **Root term**: `ZP:0000000`


### FBCV

- **ID**: `fbcv`
- **Mirror From**: [http://purl.obolibrary.org/obo/dpo.owl](http://purl.obolibrary.org/obo/dpo.owl)

- **Root term**: `FBcv:0001347`


### XPO

- **ID**: `xpo`
- **Mirror From**: [http://purl.obolibrary.org/obo/xpo.owl](http://purl.obolibrary.org/obo/xpo.owl)

- **Root term**: `XPO:00000000`



## Semantic Similarity Profiles



### HP-MP (phenio-release), semsimian, with similarity threshold 0.7

- **Subset**: `hp-mp`
- **Method**: `semsimian`
- **Ontology**: `phenio-release`
- **Threshold**: `0.7`
- **Branches**:
  - **Subject**: `UPHENO:0001001`
  - **Object**: `UPHENO:0001001`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `mp`




### HP-HP (phenio-release), semsimian, with similarity threshold 0.7

- **Subset**: `hp-hp`
- **Method**: `semsimian`
- **Ontology**: `phenio-release`
- **Threshold**: `0.7`
- **Branches**:
  - **Subject**: `UPHENO:0001001`
  - **Object**: `UPHENO:0001001`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `hp`




### HP-ZP (upheno1), semsimian, with similarity threshold 0.7

- **Subset**: `hp-zp`
- **Method**: `semsimian`
- **Ontology**: `upheno1`
- **Threshold**: `0.7`
- **Branches**:
  - **Subject**: `UPHENO:0001001`
  - **Object**: `UPHENO:0001001`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `zp`




### HP-HP (phenio-monarch), semsimian, with similarity threshold 0.7

- **Subset**: `hp-hp`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `hp`


- **IC**: `phenio_monarch_hp_ic.tsv`



### HP-MP (phenio-monarch), semsimian, with similarity threshold 0.7

- **Subset**: `hp-mp`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `mp`


- **IC**: `phenio_monarch_hp_mp_ic.tsv`



### HP-ZP (phenio-monarch), semsimian, with similarity threshold 0.7

- **Subset**: `hp-zp`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `zp`


- **IC**: `phenio_monarch_hp_zp_ic.tsv`



### HP-XPO (phenio-monarch), semsimian, with similarity threshold 0.4

- **Subset**: `hp-xpo`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.4`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `xpo`


- **IC**: `phenio_monarch_hp_xpo_ic.tsv`



### HP-HP (phenio-monarch), semsimian, with similarity threshold 0.4

- **Subset**: `hp-hp`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.4`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `hp`




### HP-MP (phenio-monarch), semsimian, with similarity threshold 0.4

- **Subset**: `hp-mp`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.4`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `mp`




### HP-ZP (phenio-monarch), semsimian, with similarity threshold 0.4

- **Subset**: `hp-zp`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.4`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `zp`




### HP-XPO (phenio-monarch), semsimian, with similarity threshold 0.4

- **Subset**: `hp-xpo`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.4`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `xpo`




### HP-HP (phenio-monarch), semsimian, with similarity threshold 0.7

- **Subset**: `hp-hp`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `hp`




### HP-MP (phenio-monarch), semsimian, with similarity threshold 0.7

- **Subset**: `hp-mp`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `mp`




### HP-ZP (phenio-monarch), semsimian, with similarity threshold 0.7

- **Subset**: `hp-zp`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `zp`




### HP-XPO (phenio-monarch), semsimian, with similarity threshold 0.7

- **Subset**: `hp-xpo`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `xpo`




### HP-FBCV (phenio-monarch), semsimian, with similarity threshold 0.4

- **Subset**: `hp-fbcv`
- **Method**: `semsimian`
- **Ontology**: `phenio-monarch`
- **Threshold**: `0.4`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `fbcv`




### HP-HP (phenio-flat), semsimian, with similarity threshold 0.7

- **Subset**: `hp-hp`
- **Method**: `semsimian`
- **Ontology**: `phenio-flat`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `hp`




### HP-MP (phenio-flat), semsimian, with similarity threshold 0.7

- **Subset**: `hp-mp`
- **Method**: `semsimian`
- **Ontology**: `phenio-flat`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `mp`




### HP-ZP (phenio-flat), semsimian, with similarity threshold 0.7

- **Subset**: `hp-zp`
- **Method**: `semsimian`
- **Ontology**: `phenio-flat`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `zp`




### HP-HP (phenio-equivalent), semsimian, with similarity threshold 0.7

- **Subset**: `hp-hp`
- **Method**: `semsimian`
- **Ontology**: `phenio-equivalent`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `hp`




### HP-MP (phenio-equivalent), semsimian, with similarity threshold 0.7

- **Subset**: `hp-mp`
- **Method**: `semsimian`
- **Ontology**: `phenio-equivalent`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `mp`




### HP-ZP (phenio-equivalent), semsimian, with similarity threshold 0.7

- **Subset**: `hp-zp`
- **Method**: `semsimian`
- **Ontology**: `phenio-equivalent`
- **Threshold**: `0.7`

- **Prefixes**:
  - **Subject**: `hp`
  - **Object**: `zp`




