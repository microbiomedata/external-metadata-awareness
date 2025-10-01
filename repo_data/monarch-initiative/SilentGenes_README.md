# Silent genes

[![Java CI with Maven](https://github.com/monarch-initiative/SilentGenes/workflows/Java%20CI%20with%20Maven/badge.svg)](https://github.com/monarch-initiative/SilentGenes/actions/workflows/maven.yml)
[![Maven Central](https://maven-badges.herokuapp.com/maven-central/org.monarchinitiative.sgenes/SilentGenes/badge.svg)](https://maven-badges.herokuapp.com/maven-central/org.monarchinitiative.sgenes/SilentGenes)

"Silent companion" library for performing genome arithmetics with genes and transcripts using _[Svart](https://github.com/exomiser/svart)_. 

_Silent genes_ defines models of genes and transcripts. Transcript definitions can be sourced from [Gencode consortium](https://www.gencodegenes.org/), or [Jannovar](https://github.com/charite/jannovar). The definitions can be stored in JSON format. _Silent genes_ works with Java 11 or better.

The project is currently in *pre-alpha* stage.

## Library structure

*Silent genes* consists of several modules:

- `silent-genes-model` provides a model of genes, transcripts, and their associated IDs,
- `silent-genes-io` for serializing `Gene`s and `Transcript`s in the internal data format into a JSON file to avoid the costly Q/C,
- `silent-genes-gtf` parses GTF file issued by [Gencode consortium](https://www.gencodegenes.org/) or [NCBI Reference Sequence project](https://www.ncbi.nlm.nih.gov/refseq),
- `silent-genes-jannovar` converts genes and transcripts from the [Jannovar](https://github.com/charite/jannovar) transcript databases into _Silent genes_ format, 
- `silent-genes-simple` gives a handful of real-life genes, mostly useful for unit testing, and
- `silent-genes-cli` command-line interface for converting genes into the internal data format.

## Command-line interface (CLI)

_Silent genes_ offeres CLI for converting gene and transcript definitions into the internal format. The following 
sources of genes and transcripts are supported:

- _Gencode_ (GTF) - genes provided by [Gencode consortium](https://www.gencodegenes.org/)
- _RefSeq_ (GTF) - genes defined by [NCBI Reference Sequence](https://www.ncbi.nlm.nih.gov/refseq) (RefSeq) project
- _Jannovar_ - [Jannovar](https://github.com/charite/jannovar) is a Java tool for functional annotation of genomic variants identified in NGS experiments, and it uses transcripts defined by _RefSeq_, _ENSEMBL_, and _UCSC_.

### Convert Gencode genes into _Silent genes_ format

Use `parse-gencode` to convert Gencode genes:

```bash
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_39/gencode.v39.basic.annotation.gtf.gz
java -jar silent-genes-cli.jar parse-gencode gencode.v39.basic.annotation.gtf.gz gencode.sg.json.gz
```

### Convert Refseq genes into _Silent genes_ format

Use `parse-refseq` to perform the conversion:

```bash
wget https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/annotation_releases/109.20211119/GCF_000001405.39_GRCh38.p13/GCF_000001405.39_GRCh38.p13_genomic.gtf.gz
java -jar silent-genes-cli.jar parse-refseq GCF_000001405.39_GRCh38.p13_genomic.gtf.gz refseq.sg.json.gz
```

## Code examples

The next paragraphs show how to use _Silent genes_ as a library in other Java application.

### Parse Gencode GTF file into a list of genes

First, get the latest GTF file from [Gencode downloads](https://www.gencodegenes.org/human/): 
```bash
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_38/gencode.v38.basic.annotation.gtf.gz
```

Next, read the GTF file into a list of `GencodeGene`s: 
```java
@Test
public void parseGencodeGtfFile() {
    Path gencodeGtf = Path.of("gencode.v38.basic.annotation.gtf.gz");
    GtfGeneParser<GencodeGene> gencodeParser = GtfGeneParserFactory.gencodeGeneParser(gencodeGtf, GenomicAssemblies.GRCh38p13());
    List<GencodeGene> genes = gencodeParser.stream().collect(Collectors.toUnmodifiableList());
    
    assertThat(genes, hasSize(63_116));
}
```

### Parse RefSeq GTF file into a list of genes

Get the latest GTF file from [RefSeq downloads](https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/annotation_releases):
```bash
wget https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/annotation_releases/109.20211119/GCF_000001405.39_GRCh38.p13/GCF_000001405.39_GRCh38.p13_genomic.gtf.gz
```

Next, read the GTF file into a list of `RefseqGene`s:
```java
@Test
public void parseRefseqGtfFile() {
    Path refseqGtf = Path.of("GCF_000001405.39_GRCh38.p13_genomic.gtf.gz");
    GtfGeneParser<RefseqGene> refseqParser = GtfGeneParserFactory.refseqGtfParser(refseqGtf, GenomicAssemblies.GRCh38p13());
    List<RefseqGene> genes = refseqParser.stream().collect(Collectors.toUnmodifiableList());
}
```

### Serialize genes into compressed JSON

The `silent-genes-io` module provides `GeneParser`s for (de)serializing `Gene`s into flat files. Currently, only JSON 
format is supported.

```java
@Test
public void serializeGenesIntoCompressedJson() {
    List<? extends Gene> genes = ... ; // start with a list of genes, e.g. from the example above
    GeneParserFactory factory = GeneParserFactory.of(GenomicAssemblies.GRCh38p13());
    GeneParser parser = factory.forFormat(SerializationFormat.JSON);

    Path destination = Path.of("genes.json.gz");
    parser.write(genes, destination);
    }
}
```

The `genes.json.gz` file with ~63k genes prepared above takes ~9MB of disk space.

### Load the genes from compressed JSON

Load the list of genes from the JSON file created above.

```java
@Test
public void deserializeGenes() {
    GeneParserFactory factory = GeneParserFactory.of(GenomicAssemblies.GRCh38p13());
    GeneParser parser = factory.forFormat(SerializationFormat.JSON);

    Path jsonPath = Path.of("genes.json.gz");
    List<? extends Gene> genes = parser.read(jsonPath);
}
```
