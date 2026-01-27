# human-cell-atlas

EXPERIMENTAL translation of HCA

Caveat: this schema is entirely constructed via an automated import of the HCA json schema.

- there may be parts missing
- the direct mapping may not utilitize key parts of LinkML

## Website

* [https://cmungall.github.io/human-cell-atlas](https://cmungall.github.io/human-cell-atlas)

The above is generated entirely from the schema, which comes from the json schema; as such
it may be spare on details.

This is also using the older linkml documentation framework, which doesn't show all the schema

## Schema

* [src/human_cell_atlas/schema](src/human_cell_atlas/schema) 

## How this was made

This was created using [schema-automator](https://github.com/linkml/schema-automator/)

Utilizing the following HCA-specific extensions

- mapping of `user_friendly` to `linkml:title`
- mapping HCA ontology extensions to [dyanamic enums](https://linkml.io/linkml/schemas/enums.html#dynamic-enums)

The following modifications were made:

- Changed “10x” to “S10x” (because otherwise this creates awkward incompatibilities between the generated python classes and the schema)
- Modified hca/system/links.json to avoid name clashes with SupplementaryFile

## Treatment of Links

I need to figure out exactly how the system/links schema is used in HCA. Currently it doesn't "connect up" to the rest of the schema.

It seems that some kind of extra-schema information is required

## Ontology Enums

All plain json enums are mapped to LinkML enums. Note that we elected not to inline these, so there are a lot of "trivial" enums with one value where the
intent is to restrict the value of a field.

In future, the permissible values could be mapped to ontology terms, but this info isn't in the schema.

HCA also uses a JSON schema extension for ontology enums, these are converted to LinkML dynamic enums, as below

### Examples

* [src/human_cell_atlas/schema//module/ontology/development_stage_ontology.yaml](src/human_cell_atlas/schema//module/ontology/development_stage_ontology.yaml)

LinkML:

```yaml
  DevelopmentStageOntology_ontology_options:
    include:
    - reachable_from:
        source_ontology: obo:efo
        source_nodes:
        - EFO:0000399
        - HsapDv:0000000
        - UBERON:0000105
        relationship_types:
        - rdfs:subClassOf
        is_direct: false
        include_self: false
    - reachable_from:
        source_ontology: obo:hcao
        source_nodes:
        - EFO:0000399
        - HsapDv:0000000
        - UBERON:0000105
        relationship_types:
        - rdfs:subClassOf
        is_direct: false
        include_self: false
```

from:

```json
"ontology": {
            "description": "An ontology term identifier in the form prefix:accession.",
            "type": "string",
            "graph_restriction":  {
                "ontologies" : ["obo:efo", "obo:hcao"],
                "classes": ["EFO:0000399", "HsapDv:0000000", "UBERON:0000105"],
                "relations": ["rdfs:subClassOf"],
                "direct": false,
                "include_self": false
            },
```

note the mapping is not quite direct. A seperate query is generated in linkml for each input ontology, where the
input seeds are repeated each time (`include` takes the union of all subqueries)

I believe the semantics are the same as for the source, although some combos will yield empty sets?

The more natural way to author this in linkml would be to make the classes specific to each subquery.

## Materialized Ontology Enums

See [value set toolkit](https://github.com/INCATools/ontology-access-kit/releases/tag/v0.1.58)

To expand value sets:

`poetry run sh utils/expand-value-sets.sh`

This materializes the value set queries, so that:

- normal non-extended json-schema tooling can use them
- query results can be versioned alongside releases

These are included alongside as `<NAME>.expanded.yaml`

File sizes:

| Value Set| Expanded | File Size |
| ---| --- | --- |
| [enrichment_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [enrichment_ontology expanded](src/human_cell_atlas/schema/module/ontology/enrichment_ontology.expanded.yaml) | 4.0K|
| [organ_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [organ_ontology expanded](src/human_cell_atlas/schema/module/ontology/organ_ontology.expanded.yaml) | 1.5M|
| [cell_cycle_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [cell_cycle_ontology expanded](src/human_cell_atlas/schema/module/ontology/cell_cycle_ontology.expanded.yaml) | 8.0K|
| [biological_macromolecule_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [biological_macromolecule_ontology expanded](src/human_cell_atlas/schema/module/ontology/biological_macromolecule_ontology.expanded.yaml) | 12K|
| [sequencing_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [sequencing_ontology expanded](src/human_cell_atlas/schema/module/ontology/sequencing_ontology.expanded.yaml) | 60K|
| [protocol_type_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [protocol_type_ontology expanded](src/human_cell_atlas/schema/module/ontology/protocol_type_ontology.expanded.yaml) | 16K|
| [species_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [species_ontology expanded](src/human_cell_atlas/schema/module/ontology/species_ontology.expanded.yaml) | 215M|
| [development_stage_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [development_stage_ontology expanded](src/human_cell_atlas/schema/module/ontology/development_stage_ontology.expanded.yaml) | 64K|
| [target_pathway_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [target_pathway_ontology expanded](src/human_cell_atlas/schema/module/ontology/target_pathway_ontology.expanded.yaml) | 108K|
| [disease_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [disease_ontology expanded](src/human_cell_atlas/schema/module/ontology/disease_ontology.expanded.yaml) | 4.8M|
| [strain_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [strain_ontology expanded](src/human_cell_atlas/schema/module/ontology/strain_ontology.expanded.yaml) | 16K|
| [file_content_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [file_content_ontology expanded](src/human_cell_atlas/schema/module/ontology/file_content_ontology.expanded.yaml) | 512K|
| [library_construction_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [library_construction_ontology expanded](src/human_cell_atlas/schema/module/ontology/library_construction_ontology.expanded.yaml) | 12K|
| [contributor_role_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [contributor_role_ontology expanded](src/human_cell_atlas/schema/module/ontology/contributor_role_ontology.expanded.yaml) | 24K|
| [mass_unit_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [mass_unit_ontology expanded](src/human_cell_atlas/schema/module/ontology/mass_unit_ontology.expanded.yaml) | 8.0K|
| [cell_type_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [cell_type_ontology expanded](src/human_cell_atlas/schema/module/ontology/cell_type_ontology.expanded.yaml) | 316K|
| [library_amplification_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [library_amplification_ontology expanded](src/human_cell_atlas/schema/module/ontology/library_amplification_ontology.expanded.yaml) | 4.0K|
| [microscopy_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [microscopy_ontology expanded](src/human_cell_atlas/schema/module/ontology/microscopy_ontology.expanded.yaml) | 8.0K|
| [ethnicity_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [ethnicity_ontology expanded](src/human_cell_atlas/schema/module/ontology/ethnicity_ontology.expanded.yaml) | 36K|
| [organ_part_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [organ_part_ontology expanded](src/human_cell_atlas/schema/module/ontology/organ_part_ontology.expanded.yaml) | 1.5M|
| [treatment_method_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [treatment_method_ontology expanded](src/human_cell_atlas/schema/module/ontology/treatment_method_ontology.expanded.yaml) | 296K|
| [process_type_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [process_type_ontology expanded](src/human_cell_atlas/schema/module/ontology/process_type_ontology.expanded.yaml) | 84K|
| [time_unit_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [time_unit_ontology expanded](src/human_cell_atlas/schema/module/ontology/time_unit_ontology.expanded.yaml) | 4.0K|
| [file_format_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [file_format_ontology expanded](src/human_cell_atlas/schema/module/ontology/file_format_ontology.expanded.yaml) | 4.0K|
| [instrument_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [instrument_ontology expanded](src/human_cell_atlas/schema/module/ontology/instrument_ontology.expanded.yaml) | 12K|
| [cellular_component_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [cellular_component_ontology expanded](src/human_cell_atlas/schema/module/ontology/cellular_component_ontology.expanded.yaml) | 480K|
| [length_unit_ontology](src/human_cell_atlas/schema/module/ontology/.yaml) | [length_unit_ontology expanded](src/human_cell_atlas/schema/module/ontology/length_unit_ontology.expanded.yaml) | 8.0K|

Note in particular that the species expanded subset in a quarter of a gigabyte...

Some of the expanded sets may be empty due to a mismatch in how HCA and OAK use CURIEs for EDAM

## Repository Structure

* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
    * [human_cell_atlas](src/human_cell_atlas)
        * [schema](src/human_cell_atlas/schema) -- LinkML schema (generated from HCA)
* [datamodel](src/human_cell_atlas/datamodel) -- Generated python datamodel
* [tests](tests/) - python tests

## Developer Documentation

<details>
Use the `make` command to generate project artefacts:

- `make all`: make everything
- `make deploy`: deploys site

</details>

## Credits

this project was made with [linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter)
