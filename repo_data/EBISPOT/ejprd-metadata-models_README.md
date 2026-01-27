# Metadata for EJP rare disease patient registries, biobanks and catalogs

This is for publishing [European Joint Programme (EJP) for Rare Disease](http://www.ejprarediseases.org) virtual platform metadata for Biobanks and Catalogs metadata, through the  extraction, conversion, RDF schema and validating the data RDF data using the ShExC.

 We are also working to align with similar schema standardisation efforts such as [RD connect semantic model](https://github.com/LUMC-BioSemantics/Rare-Disease-Semantic-Model), [schema.org](https://schema.org), [bioschemas](https://bioschemas.org), [MIABIS](https://github.com/MIABIS/miabis/wiki) and [GA4GH](https://www.ga4gh.org) (see also [schema blocks](https://schemablocks.org) and [phenopackets](http://phenopackets.org). A proposed semantic model for the Common Data Elements can be found [here](https://github.com/LUMC-BioSemantics/ERN-common-data-elements).

This diagram illustrates the basic idea of the metadata publication workflow. Components are independent and can be used and new blocks can be defined that inherit from parent blocks.

For more details on the metadata see the [WIKI page](https://github.com/EBISPOT/ejprd-metadata-models/wiki/European-Joint-Programme-(EJP)-for-Rare-Disease-Virtual-Platform-Metadata-Model)

# EJPRD namespace nomenclature
* The scheme : https
* The authority: https://www.ejprarediseases.org/
* The path : "/"
* The fragment: starts with "#"
* For defining ejprd vocabulary : https://www.ejprarediseases.org/metdata/core
* For defining the ejprd classes: https://www.ejprarediseases.org/metadata/core#ClassesA
* For defining the ejprd properties: https://www.ejprarediseases.org/metadata/core#PropertiesA


# WORKFLOW FOR EJP-RD METADATA PUBLISHING
![schema](https://github.com/S2Ola/ejprd-metadata-model/blob/master/images/EJP-RD-Metadata.png)
This is the entire codebase for the EJP-RD Metadata publishers. The model is based on and builds on existing standards, such as the [European Rare Disease Registry Infrastructure](https://eu-rd-platform.jrc.ec.europa.eu) and the [Common Data Elements](http://www.erare.eu/sites/default/files/SetCommonData-EU%20RD%20Platform_CDS%20_final.pdf) from the rare disease community and other more generalised standards for data sharing such as the W3C [DCAT vocabulary](https://www.w3.org/TR/vocab-dcat/).

EJP-RD Metadata standard is build around two major standards - [JSON](https://json-schema.org/) and [RDF](https://www.w3.org/RDF/) standard models for data exchange.

#Validators:
 * JSON Schema tool for validating the structure of JSON data, from the various registries, biobanks, or etc through the API or Web URL.

 * RDF schema tool for validating the RDF graph

 * ShEx Schema tool for validating the RDF graph data

The metadata core schema as shown for the EJP_RD virtual platform(VP) displayed below:
##  Metadata core schema for VP
![Metadata vp_model](https://github.com/S2Ola/ejprd-metadata-model/blob/master/images/vp_model.gif)

##  EJP-RD Catalog schema blocks
![EJP schema blocks](https://github.com/S2Ola/ejprd-metadata-model/blob/master/images/ejprdSchemaBlocks.png)


* The EJP-RD VP Catalog Schema in JSON format
  * The Catalog Entity [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/catalog.json)
  * The Catalog-Patient-Registry [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/catalog-patientregistry.json)
  * The Catalog-BioBank [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/catalog-biobank.json)
  * The StudyDesign [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/studydesign.json)
  * The Biological-Sample [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/BiologicalSample.json)
  * The Biological-Sample-Patient [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/bioslogicalSamplePatient.json)
  * The Organisation [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/organisation.json)
  * The Date-Time [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/datetime.json)
  * The Property-Value [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/propertyvalue.json)
  * The Location [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/location.json)
  * The EUPID [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/eupid.json)
  * The Code [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/code.json)
  * The Coding-System [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/json_files/codingSystem.json)

  ##  EJP-RD Data format converter (JSON to RDF) workflow
  ![EJP-RD Data Converter JSON to RDF Workflow ](https://github.com/S2Ola/ejprd-metadata-model/blob/master/images/JSON2RDFWRKFLOW.jpg)

* The Validators - ShEx Constrains Schemas
  * The ShExC for Catalog-BioBank [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/shex_schema/ShExJ/Catalog-BioBank-shape)
  * The ShExC for Catalog [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/shex_schema/ShExJ/catalog_shape)
  * The ShExC for Catalog-PatientRegistry [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/shex_schema/ShExJ/catalog-patient-registryshape)
  * The ShExC for EJP-RD Metadata Core [here](https://github.com/S2Ola/ejprd-metadata-model/blob/master/shex_schema/ShExJ/ejprd-metadata-shape)

* The JSON to RDF converter [here](https://github.com/S2Ola/ejprd-metadata-model/tree/master/JSON2RDF)

  The jar file can be invoke from the command line using the following command :
  " cat "filename".json | java -jar json2rdf.jar https://www.ejprarediseases.org/metadata# | riot --formatted=TURTLE "
