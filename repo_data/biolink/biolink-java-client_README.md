# swagger-java-client

## Requirements

Building the API client library requires [Maven](https://maven.apache.org/) to be installed.

## Installation

To install the API client library to your local Maven repository, simply execute:

```shell
mvn install
```

To deploy it to a remote Maven repository instead, configure the settings of the repository and execute:

```shell
mvn deploy
```

Refer to the [official documentation](https://maven.apache.org/plugins/maven-deploy-plugin/usage.html) for more information.

### Maven users

Add this dependency to your project's POM:

```xml
<dependency>
    <groupId>io.swagger</groupId>
    <artifactId>swagger-java-client</artifactId>
    <version>1.0.0</version>
    <scope>compile</scope>
</dependency>
```

### Gradle users

Add this dependency to your project's build file:

```groovy
compile "io.swagger:swagger-java-client:1.0.0"
```

### Others

At first generate the JAR by executing:

    mvn package

Then manually install the following JARs:

* target/swagger-java-client-1.0.0.jar
* target/lib/*.jar

## Getting Started

Please follow the [installation](#installation) instruction and execute the following Java code:

```java

import io.swagger.client.*;
import io.swagger.client.auth.*;
import io.swagger.client.model.*;
import io.swagger.client.api.AssociationApi;

import java.io.File;
import java.util.*;

public class AssociationApiExample {

    public static void main(String[] args) {
        
        AssociationApi apiInstance = new AssociationApi();
        String id = "id_example"; // String | 
        Integer rows = 10; // Integer | number of rows
        Boolean flExcludesEvidence = true; // Boolean | If set, excludes evidence objects in response
        String evidence = "evidence_example"; // String | Object id, e.g. ECO:0000501 (for IEA; Includes inferred by default)                     or a specific publication or other supporting ibject, e.g. ZFIN:ZDB-PUB-060503-2.                     
        Integer page = 1; // Integer | Page number
        String object = "object_example"; // String | OBJECT id, e.g. HP:0011927. Includes inferred by default
        String subject = "subject_example"; // String | SUBJECT id, e.g. NCBIGene:84570, ZFIN:ZDB-GENE-050417-357. Includes inferred by default
        String subjectTaxon = "subjectTaxon_example"; // String | SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default
        Boolean graphize = true; // Boolean | If set, includes graph object in response
        String mapIdentifiers = "mapIdentifiers_example"; // String | Prefix to map all IDs to. E.g. NCBIGene
        try {
            List<Association> result = apiInstance.getAssociationObject(id, rows, flExcludesEvidence, evidence, page, object, subject, subjectTaxon, graphize, mapIdentifiers);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AssociationApi#getAssociationObject");
            e.printStackTrace();
        }
    }
}

```

## Documentation for API Endpoints

All URIs are relative to *https://localhost/api*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AssociationApi* | [**getAssociationObject**](docs/AssociationApi.md#getAssociationObject) | **GET** /association/{id} | Returns the association with a given identifier
*AssociationApi* | [**getAssociationSearch**](docs/AssociationApi.md#getAssociationSearch) | **GET** /association/find/ | Returns list of matching associations
*AssociationApi* | [**getAssociationSearch_0**](docs/AssociationApi.md#getAssociationSearch_0) | **GET** /association/find/{subject_category}/ | Returns list of matching associations
*AssociationApi* | [**getAssociationSearch_1**](docs/AssociationApi.md#getAssociationSearch_1) | **GET** /association/find/{subject_category}/{object_category}/ | Returns list of matching associations
*AssociationApi* | [**getAssociationsFrom**](docs/AssociationApi.md#getAssociationsFrom) | **GET** /association/between/{subject}/{object} | Returns associations connecting two entities
*AssociationApi* | [**getAssociationsFrom_0**](docs/AssociationApi.md#getAssociationsFrom_0) | **GET** /association/from/{subject} | Returns list of matching associations
*AssociationApi* | [**getAssociationsTo**](docs/AssociationApi.md#getAssociationsTo) | **GET** /association/to/{object} | Returns list of matching associations
*BioentityApi* | [**getAlleleObject**](docs/BioentityApi.md#getAlleleObject) | **GET** /bioentity/allele/{id} | TODO Returns allele object
*BioentityApi* | [**getAnatomyGeneAssociations**](docs/BioentityApi.md#getAnatomyGeneAssociations) | **GET** /bioentity/anatomy/{id}/genes/ | TODO Returns associations between anatomical entity and genes
*BioentityApi* | [**getAnatomyObject**](docs/BioentityApi.md#getAnatomyObject) | **GET** /bioentity/anatomy/{id} | TODO Returns anatomical entity
*BioentityApi* | [**getAnatomyPhenotypeAssociations**](docs/BioentityApi.md#getAnatomyPhenotypeAssociations) | **GET** /bioentity/anatomy/{id}/phenotypes/ | TODO Returns associations between anatomical entity and phenotypes
*BioentityApi* | [**getDiseaseAnatomyAssociations**](docs/BioentityApi.md#getDiseaseAnatomyAssociations) | **GET** /bioentity/disease/{id}/anatomy/ | TODO Returns anatomical locations associated with a disease
*BioentityApi* | [**getDiseaseFunctionAssociations**](docs/BioentityApi.md#getDiseaseFunctionAssociations) | **GET** /bioentity/disease/{id}/function/ | TODO Returns biological functions associated with a disease
*BioentityApi* | [**getDiseaseGeneAssociations**](docs/BioentityApi.md#getDiseaseGeneAssociations) | **GET** /bioentity/disease/{id}/genes/ | Returns genes associated with a disease
*BioentityApi* | [**getDiseaseModelAssociations**](docs/BioentityApi.md#getDiseaseModelAssociations) | **GET** /bioentity/disease/{id}/models/ | Returns associations to models of the disease
*BioentityApi* | [**getDiseaseModelTaxonAssociations**](docs/BioentityApi.md#getDiseaseModelTaxonAssociations) | **GET** /bioentity/disease/{id}/models/{taxon} | Same as &#x60;/disease/&lt;id&gt;/models&#x60; but constrain models by taxon
*BioentityApi* | [**getDiseaseObject**](docs/BioentityApi.md#getDiseaseObject) | **GET** /bioentity/disease/{id} | TODO Returns disease object
*BioentityApi* | [**getDiseasePhenotypeAssociations**](docs/BioentityApi.md#getDiseasePhenotypeAssociations) | **GET** /bioentity/disease/{id}/phenotypes/ | Returns phenotypes associated with disease
*BioentityApi* | [**getDiseaseSubstanceAssociations**](docs/BioentityApi.md#getDiseaseSubstanceAssociations) | **GET** /bioentity/disease/{id}/substance/ | Returns substances associated with a disease
*BioentityApi* | [**getDiseaseSubstanceAssociations_0**](docs/BioentityApi.md#getDiseaseSubstanceAssociations_0) | **GET** /bioentity/substance/{id}/treats/ | Returns substances associated with a disease
*BioentityApi* | [**getEnvironmentObject**](docs/BioentityApi.md#getEnvironmentObject) | **GET** /bioentity/environment/{id} | TODO Returns environment entity
*BioentityApi* | [**getEnvironmentPhenotypeAssociations**](docs/BioentityApi.md#getEnvironmentPhenotypeAssociations) | **GET** /bioentity/environment/{id}/phenotypes/ | TODO Returns list of associations
*BioentityApi* | [**getGeneExpressionAssociations**](docs/BioentityApi.md#getGeneExpressionAssociations) | **GET** /bioentity/gene/{id}/expressed/ | TODO Returns expression events for a gene
*BioentityApi* | [**getGeneFunctionAssociations**](docs/BioentityApi.md#getGeneFunctionAssociations) | **GET** /bioentity/gene/{id}/function/ | Returns function associations for a gene
*BioentityApi* | [**getGeneHomologAssociations**](docs/BioentityApi.md#getGeneHomologAssociations) | **GET** /bioentity/gene/{id}/homologs/ | Returns homologs for a gene
*BioentityApi* | [**getGeneInteractions**](docs/BioentityApi.md#getGeneInteractions) | **GET** /bioentity/gene/{id}/interactions/ | Returns interactions for a gene
*BioentityApi* | [**getGeneObject**](docs/BioentityApi.md#getGeneObject) | **GET** /bioentity/gene/{id} | Returns gene object
*BioentityApi* | [**getGenePhenotypeAssociations**](docs/BioentityApi.md#getGenePhenotypeAssociations) | **GET** /bioentity/gene/{id}/phenotypes/ | Returns phenotypes associated with gene
*BioentityApi* | [**getGenePublicationList**](docs/BioentityApi.md#getGenePublicationList) | **GET** /bioentity/gene/{id}/pubs/ | TODO Returns expression events for a gene
*BioentityApi* | [**getGeneproductObject**](docs/BioentityApi.md#getGeneproductObject) | **GET** /bioentity/geneproduct/{id} | TODO Returns gene product object
*BioentityApi* | [**getGenericAssociations**](docs/BioentityApi.md#getGenericAssociations) | **GET** /bioentity/{id}/associations/ | Returns associations for an entity regardless of the type
*BioentityApi* | [**getGenericObject**](docs/BioentityApi.md#getGenericObject) | **GET** /bioentity/{id} | TODO Returns object of any type
*BioentityApi* | [**getGenotypeDiseaseAssociations**](docs/BioentityApi.md#getGenotypeDiseaseAssociations) | **GET** /bioentity/genotype/{id}/diseases/ | Returns diseases associated with a genotype
*BioentityApi* | [**getGenotypeGeneAssociations**](docs/BioentityApi.md#getGenotypeGeneAssociations) | **GET** /bioentity/genotype/{id}/genes/ | Returns genes associated with a genotype
*BioentityApi* | [**getGenotypeGenotypeAssociations**](docs/BioentityApi.md#getGenotypeGenotypeAssociations) | **GET** /bioentity/genotype/{id}/genotypes/ | Returns genotypes-genotype associations
*BioentityApi* | [**getGenotypeObject**](docs/BioentityApi.md#getGenotypeObject) | **GET** /bioentity/genotype/{id} | Returns genotype object
*BioentityApi* | [**getGenotypePhenotypeAssociations**](docs/BioentityApi.md#getGenotypePhenotypeAssociations) | **GET** /bioentity/genotype/{id}/phenotypes/ | Returns phenotypes associated with a genotype
*BioentityApi* | [**getGotermGeneAssociations**](docs/BioentityApi.md#getGotermGeneAssociations) | **GET** /bioentity/goterm/{id}/genes/ | TODO Returns associated phenotypes
*BioentityApi* | [**getGotermObject**](docs/BioentityApi.md#getGotermObject) | **GET** /bioentity/goterm/{id} | TODO Returns GO class object
*BioentityApi* | [**getGotermPhenotypeAssociations**](docs/BioentityApi.md#getGotermPhenotypeAssociations) | **GET** /bioentity/goterm/{id}/phenotype/ | TODO Returns associated phenotypes
*BioentityApi* | [**getLiteratureDiseaseAssociations**](docs/BioentityApi.md#getLiteratureDiseaseAssociations) | **GET** /bioentity/literature/{id}/diseases/ | Returns associations between a lit entity and a disease
*BioentityApi* | [**getLiteratureGeneAssociations**](docs/BioentityApi.md#getLiteratureGeneAssociations) | **GET** /bioentity/literature/{id}/genes/ | Returns associations between a lit entity and a gene
*BioentityApi* | [**getLiteratureGenotypeAssociations**](docs/BioentityApi.md#getLiteratureGenotypeAssociations) | **GET** /bioentity/literature/{id}/genotypes/ | Returns associations between a lit entity and a genotype
*BioentityApi* | [**getParentObject**](docs/BioentityApi.md#getParentObject) | **GET** /bioentity/individual/{id} | TODO Returns individual
*BioentityApi* | [**getParentObject_0**](docs/BioentityApi.md#getParentObject_0) | **GET** /bioentity/investigation/{id} | TODO Returns investigation object
*BioentityApi* | [**getPathwayGeneAssociations**](docs/BioentityApi.md#getPathwayGeneAssociations) | **GET** /bioentity/pathway/{id}/genes/ | TODO Returns list of genes associated with a pathway
*BioentityApi* | [**getPathwayObject**](docs/BioentityApi.md#getPathwayObject) | **GET** /bioentity/pathway/{id} | TODO Returns pathway object
*BioentityApi* | [**getPathwayParticipantAssociations**](docs/BioentityApi.md#getPathwayParticipantAssociations) | **GET** /bioentity/pathway/{id}/participants/ | TODO Returns associations to participants (molecules, etc) for a pathway
*BioentityApi* | [**getPhenotypeAnatomyAssociations**](docs/BioentityApi.md#getPhenotypeAnatomyAssociations) | **GET** /bioentity/phenotype/{id}/anatomy/ | Returns anatomical entities associated with a phenotype
*BioentityApi* | [**getPhenotypeFunctionAssociations**](docs/BioentityApi.md#getPhenotypeFunctionAssociations) | **GET** /bioentity/phenotype/{id}/function/ | TODO Returns biological functions associated with a Phenotype
*BioentityApi* | [**getPhenotypeGeneAssociations**](docs/BioentityApi.md#getPhenotypeGeneAssociations) | **GET** /bioentity/phenotype/{id}/gene/{taxid}/ids | Returns gene ids for all genes for a particular phenotype in a taxon
*BioentityApi* | [**getPhenotypeGeneAssociations_0**](docs/BioentityApi.md#getPhenotypeGeneAssociations_0) | **GET** /bioentity/phenotype/{id}/genes/ | TODO Returns associated phenotypes
*BioentityApi* | [**getPhenotypeObject**](docs/BioentityApi.md#getPhenotypeObject) | **GET** /bioentity/phenotype/{id} | TODO Returns phenotype class object
*BioentityApi* | [**getPhenotypePhenotypeAssociations**](docs/BioentityApi.md#getPhenotypePhenotypeAssociations) | **GET** /bioentity/phenotype/{id}/phenotype/ | TODO Returns associated phenotypes
*BioentityApi* | [**getPubObject**](docs/BioentityApi.md#getPubObject) | **GET** /bioentity/literature/{id} | TODO Returns publication object
*BioentityApi* | [**getSequenceFeatureObject**](docs/BioentityApi.md#getSequenceFeatureObject) | **GET** /bioentity/sequence_feature/{id} | TODO Returns seqfeature
*BioentityApi* | [**getSubstanceExposures**](docs/BioentityApi.md#getSubstanceExposures) | **GET** /bioentity/substance/{id}/exposures/ | TODO Returns associations between a substance and related exposures
*BioentityApi* | [**getSubstanceInteractions**](docs/BioentityApi.md#getSubstanceInteractions) | **GET** /bioentity/substance/{id}/interactions/ | TODO Returns associations between given drug and interactions
*BioentityApi* | [**getSubstanceObject**](docs/BioentityApi.md#getSubstanceObject) | **GET** /bioentity/substance/{id} | TODO Returns substance entity
*BioentityApi* | [**getSubstanceParticipantInAssociations**](docs/BioentityApi.md#getSubstanceParticipantInAssociations) | **GET** /bioentity/substance/{id}/participant_in/ | Returns associations between an activity and process and the specified substance
*BioentityApi* | [**getSubstanceRelationships**](docs/BioentityApi.md#getSubstanceRelationships) | **GET** /bioentity/substance/{id}/substances/ | TODO Returns associations between a substance and other substances
*BioentityApi* | [**getSubstanceRoleAssociations**](docs/BioentityApi.md#getSubstanceRoleAssociations) | **GET** /bioentity/substance/{id}/roles/ | Returns associations between given drug and roles
*BioentityApi* | [**getSubstanceTargetAssociations**](docs/BioentityApi.md#getSubstanceTargetAssociations) | **GET** /bioentity/substance/{id}/targets/ | TODO Returns associations between given drug and targets
*BioentityApi* | [**getVariantGeneAssociations**](docs/BioentityApi.md#getVariantGeneAssociations) | **GET** /bioentity/variant/{id}/genes/ | Returns genes associated with a variant
*BioentityApi* | [**getVariantGenotypeAssociations**](docs/BioentityApi.md#getVariantGenotypeAssociations) | **GET** /bioentity/variant/{id}/genotypes/ | Returns genotypes associated with a variant
*BioentityApi* | [**getVariantObject**](docs/BioentityApi.md#getVariantObject) | **GET** /bioentity/variant/{id} | TODO Returns sequence variant entity
*BioentityApi* | [**getVariantPhenotypeAssociations**](docs/BioentityApi.md#getVariantPhenotypeAssociations) | **GET** /bioentity/variant/{id}/phenotypes/ | Returns phenotypes associated with a variant
*BioentitysetApi* | [**getEntitySetAssociations**](docs/BioentitysetApi.md#getEntitySetAssociations) | **GET** /bioentityset/associations/ | Returns compact associations for a given input set
*BioentitysetApi* | [**getEntitySetGraphResource**](docs/BioentitysetApi.md#getEntitySetGraphResource) | **GET** /bioentityset/graph/ | TODO Graph object spanning all entities
*BioentitysetApi* | [**getEntitySetHomologsDeprecated**](docs/BioentitysetApi.md#getEntitySetHomologsDeprecated) | **GET** /bioentityset/DEPRECATEDhomologs/ | Returns homology associations for a given input set of genes
*BioentitysetApi* | [**getEntitySetOverRepresentationAnalysis**](docs/BioentitysetApi.md#getEntitySetOverRepresentationAnalysis) | **GET** /bioentityset/ora/ | TODO Over-representation analysis
*BioentitysetApi* | [**getEntitySetOverRepresentationAnalysis_0**](docs/BioentitysetApi.md#getEntitySetOverRepresentationAnalysis_0) | **GET** /bioentityset/ora/{object_category}/ | TODO Over-representation analysis
*BioentitysetApi* | [**getEntitySetSummary**](docs/BioentitysetApi.md#getEntitySetSummary) | **GET** /bioentityset/descriptor/counts/ | Summary statistics for objects associated
*BioentitysethomologsApi* | [**getEntitySetHomologs**](docs/BioentitysethomologsApi.md#getEntitySetHomologs) | **GET** /bioentityset/homologs/homologs/ | Returns homology associations for a given input set of genes
*CamApi* | [**getActivityCollection**](docs/CamApi.md#getActivityCollection) | **GET** /cam/activity/ | Returns list of models
*CamApi* | [**getInstance**](docs/CamApi.md#getInstance) | **GET** /cam/instance/{id} | Returns list of matches
*CamApi* | [**getModel**](docs/CamApi.md#getModel) | **GET** /cam/model/{id} | Returns a complete model
*CamApi* | [**getModelCollection**](docs/CamApi.md#getModelCollection) | **GET** /cam/model/ | Returns list of ALL models
*CamApi* | [**getModelCollection_0**](docs/CamApi.md#getModelCollection_0) | **GET** /cam/model/properties/ | Returns list of all properties used across all models
*CamApi* | [**getModelCollection_1**](docs/CamApi.md#getModelCollection_1) | **GET** /cam/model/property_values/ | Returns list property-values for all models
*CamApi* | [**getModelCollection_2**](docs/CamApi.md#getModelCollection_2) | **GET** /cam/model/query/ | Returns list of models matching query
*CamApi* | [**getModelContibutors**](docs/CamApi.md#getModelContibutors) | **GET** /cam/instances/ | Returns list of all instances
*CamApi* | [**getModelContibutors_0**](docs/CamApi.md#getModelContibutors_0) | **GET** /cam/model/contributors/ | Returns list of all contributors across all models
*CamApi* | [**getPhysicalInteraction**](docs/CamApi.md#getPhysicalInteraction) | **GET** /cam/physical_interaction/ | Returns list of models
*EvidencegraphApi* | [**getAssociationObject**](docs/EvidencegraphApi.md#getAssociationObject) | **GET** /evidence/graph/{id} | Returns evidence graph object for a given association
*EvidencegraphApi* | [**getAssociationObject_0**](docs/EvidencegraphApi.md#getAssociationObject_0) | **GET** /evidence/graph/{id}/image | Returns evidence graph as a png
*GenomefeaturesApi* | [**getFeaturesWithinResource**](docs/GenomefeaturesApi.md#getFeaturesWithinResource) | **GET** /genome/features/within/{build}/{reference}/{begin}/{end} | Returns list of matches
*GraphApi* | [**getEdgeResource**](docs/GraphApi.md#getEdgeResource) | **GET** /graph/edges/from/{id} | Returns edges emanating from a node
*GraphApi* | [**getNodeResource**](docs/GraphApi.md#getNodeResource) | **GET** /graph/node/{id} | Returns a graph node
*IdentifiermapperApi* | [**getPrefixCollection**](docs/IdentifiermapperApi.md#getPrefixCollection) | **GET** /identifier/mapper/{source}/{target}/ | TODO maps a list of identifiers from a source to a target
*IdentifierprefixesApi* | [**getPrefixCollection**](docs/IdentifierprefixesApi.md#getPrefixCollection) | **GET** /identifier/prefixes/ | Returns list of prefixes
*IdentifierprefixesApi* | [**getPrefixCollection_0**](docs/IdentifierprefixesApi.md#getPrefixCollection_0) | **GET** /identifier/prefixes/contract/{uri} | Returns contracted URI
*IdentifierprefixesApi* | [**getPrefixCollection_1**](docs/IdentifierprefixesApi.md#getPrefixCollection_1) | **GET** /identifier/prefixes/expand/{id} | Returns expanded URI
*IndividualApi* | [**getIndividual**](docs/IndividualApi.md#getIndividual) | **GET** /individual/{id} | Returns list of matches
*IndividualApi* | [**getPedigree**](docs/IndividualApi.md#getPedigree) | **GET** /individual/pedigree/{id} | Returns list of matches
*NlpannotateApi* | [**getAnnotate**](docs/NlpannotateApi.md#getAnnotate) | **GET** /nlp/annotate/{text} | Returns list of matches
*OntolApi* | [**getInformationContentResource**](docs/OntolApi.md#getInformationContentResource) | **GET** /ontol/information_content/{subject_category}/{object_category}/{subject_taxon} | Calculates information content
*OntolslimmerApi* | [**getFoo**](docs/OntolslimmerApi.md#getFoo) | **GET** /ontol/slimmer/{subset} | Maps to slim
*OwlontologyApi* | [**getDlQuery**](docs/OwlontologyApi.md#getDlQuery) | **GET** /owl/ontology/dlquery/{query} | Returns list of matches
*OwlontologyApi* | [**getDlQuery_0**](docs/OwlontologyApi.md#getDlQuery_0) | **GET** /owl/ontology/sparql/{query} | Returns list of matches
*PairsimApi* | [**getPairSimJaccardResource**](docs/PairsimApi.md#getPairSimJaccardResource) | **GET** /pair/sim/jaccard/{id1}/{id2}/ | Get pairwise similarity
*PubpubsApi* | [**getFoo**](docs/PubpubsApi.md#getFoo) | **GET** /pub/pubs/{term} | Returns list of matches
*RelationusageApi* | [**getRelationUsageBetweenResource**](docs/RelationusageApi.md#getRelationUsageBetweenResource) | **GET** /relation/usage/between/{subject_category}/{object_category} | All relations used plus count of associations
*RelationusageApi* | [**getRelationUsagePivotLabelResource**](docs/RelationusageApi.md#getRelationUsagePivotLabelResource) | **GET** /relation/usage/pivot/label | Relation usage count for all subj x obj category combinations, showing label
*RelationusageApi* | [**getRelationUsagePivotResource**](docs/RelationusageApi.md#getRelationUsagePivotResource) | **GET** /relation/usage/pivot/ | Relation usage count for all subj x obj category combinations
*RelationusageApi* | [**getRelationUsageResource**](docs/RelationusageApi.md#getRelationUsageResource) | **GET** /relation/usage/ | All relations used plus count of associations
*SearchentityApi* | [**getAuthocomplete**](docs/SearchentityApi.md#getAuthocomplete) | **GET** /search/entity/autocomplete/{term} | Returns list of matches
*SearchentityApi* | [**getAuthocomplete_0**](docs/SearchentityApi.md#getAuthocomplete_0) | **GET** /search/entity/query/ | Returns list of matches
*SearchentityApi* | [**getSearchEntities**](docs/SearchentityApi.md#getSearchEntities) | **GET** /search/entity/{term} | Returns list of matches
*VariationsetApi* | [**deleteVariantSetItem**](docs/VariationsetApi.md#deleteVariantSetItem) | **DELETE** /variation/set/{id} | Deletes variant set
*VariationsetApi* | [**getAnalyze**](docs/VariationsetApi.md#getAnalyze) | **GET** /variation/set/analyze/{id} | Returns list of matches
*VariationsetApi* | [**getVariantSetItem**](docs/VariationsetApi.md#getVariantSetItem) | **GET** /variation/set/{id} | Returns a variant set
*VariationsetApi* | [**getVariantSetsArchiveCollection**](docs/VariationsetApi.md#getVariantSetsArchiveCollection) | **GET** /variation/set/archive/{year}/{month}/{day}/ | Returns list of variant sets from a specified time period
*VariationsetApi* | [**getVariantSetsCollection**](docs/VariationsetApi.md#getVariantSetsCollection) | **GET** /variation/set/ | Returns list of variant sets
*VariationsetApi* | [**postVariantSetsCollection**](docs/VariationsetApi.md#postVariantSetsCollection) | **POST** /variation/set/ | Creates a new variant set
*VariationsetApi* | [**putVariantSetItem**](docs/VariationsetApi.md#putVariantSetItem) | **PUT** /variation/set/{id} | Updates a variant set


## Documentation for Models

 - [APageOfResults](docs/APageOfResults.md)
 - [AbstractPropertyValue](docs/AbstractPropertyValue.md)
 - [Allele](docs/Allele.md)
 - [AnnotationExtension](docs/AnnotationExtension.md)
 - [Association](docs/Association.md)
 - [AssociationPropertyValue](docs/AssociationPropertyValue.md)
 - [AssociationResults](docs/AssociationResults.md)
 - [BioObject](docs/BioObject.md)
 - [Chromosome](docs/Chromosome.md)
 - [CompactAssociationSet](docs/CompactAssociationSet.md)
 - [Edge](docs/Edge.md)
 - [Exon](docs/Exon.md)
 - [Gene](docs/Gene.md)
 - [Genotype](docs/Genotype.md)
 - [Graph](docs/Graph.md)
 - [NamedObject](docs/NamedObject.md)
 - [Node](docs/Node.md)
 - [PageOfVariantSets](docs/PageOfVariantSets.md)
 - [Publication](docs/Publication.md)
 - [Relation](docs/Relation.md)
 - [SearchResult](docs/SearchResult.md)
 - [Seq](docs/Seq.md)
 - [SequenceFeature](docs/SequenceFeature.md)
 - [SequenceLocation](docs/SequenceLocation.md)
 - [SequencePosition](docs/SequencePosition.md)
 - [Substance](docs/Substance.md)
 - [SummaryPropertyValue](docs/SummaryPropertyValue.md)
 - [Taxon](docs/Taxon.md)
 - [Transcript](docs/Transcript.md)
 - [VariantSet](docs/VariantSet.md)


## Documentation for Authorization

All endpoints do not require authorization.
Authentication schemes defined for the API:

## Recommendation

It's recommended to create an instance of `ApiClient` per thread in a multithreaded environment to avoid any potential issue.

## Author



