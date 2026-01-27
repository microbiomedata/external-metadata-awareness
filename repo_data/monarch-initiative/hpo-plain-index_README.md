### HPO Plain Language Indexer

Builds a solr index of HPO plain language and clinical synonyms, including phenotype
and anatomy groupings to enable faceting.  For example:

````
[
  {
    "id": "HP:0001528",
    "label": "Hemihypertrophy",
    "definition": "Overgrowth of only one side of the body.",
    "has_pl_syn": true,
    "exact_synonym": [
      "Asymmetric overgrowth"
    ],
    "exact_syn_clin": [
      "Asymmetric limb hypertrophy"
    ],
    "phenotype_closure": [
      "HP:0001528",
      "HP:0040064",
      "HP:0100555",
      "HP:0001507",
      "HP:0000118"
    ],
    "phenotype_closure_label": [
      "Hemihypertrophy",
      "Abnormality of limbs",
      "Asymmetric growth",
      "Growth abnormality",
      "Phenotypic abnormality"
    ],
    "anatomy_closure": [
      "UBERON:0000061",
      "UBERON:0010000",
      "UBERON:0000475",
      "UBERON:0010707",
      "UBERON:0015212",
      "UBERON:0000465",
      "UBERON:0001062"
    ],
    "anatomy_closure_label": [
      "appendage girdle complex",
      "organism subdivision",
      "material anatomical entity",
      "anatomical entity",
      "anatomical structure",
      "multicellular anatomical structure",
      "lateral structure"
    ]
  }
]
````

### Building and running with Docker Compose

Build and initialize:

    docker-compose up -d

(Wait 30 seconds) Run the integration tests:

    docker-compose run loader integration-tests

Run the unit tests:

    docker-compose run loader test

Load the data (takes ~10 minutes):

    docker-compose run loader load-index
    
View the index:

    http://localhost:8983/solr/hpo-pl/select?q=*:*&wt=json

Archive and copy index to local filesystem

    docker-compose exec solr bash -c 'cd /opt/solr/server/solr && tar cfv hpo-pl.tar hpo-pl/'
    docker cp solr-hpo:/opt/solr/server/solr/hpo-pl.tar ./
    
Stop and remove containers, networks, volumes, and images
    
    docker-compose down
