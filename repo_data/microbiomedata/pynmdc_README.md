# About pynmdc

PyNMDC is a Python package to work with NMDC data.

More about NMDC: https://microbiomedata.org/

## Install (for developers only):

### Clone the repository

`git clone git@github.com:microbiomedata/pynmdc.gitc.git`

### Setup

Package intall using pypi
```sh
pynmdc$ pip install nmdc
```


Go to the pynmdc package root dir and run the following command
to install the package in developer mode,

```sh
pynmdc$ pip install -e .
```

### Test Command line interface

```
pynmdc$ nmdc --help
Usage: nmdc [OPTIONS] COMMAND [ARGS]...

  NMDC Tools v0.2.

Options:
  --help  Show this message and exit.

Commands:
  gff2json  Convert GFF3 to NMDC JSON format.
```

### Test the package

The test_data directory contains two example gff files and the corresponding JSON outputs. Note that the string `nmdc:4ce9a799923b238585fc952135e5a0f5` is an example activity id.
   
```sh

MetaG_annotation$ nmdc gff2json -of simple_feature.json -oa simple_func.json -ai nmdc:4ce9a799923b238585fc952135e5a0f5 simple_example.gff 
```

This command will generate two json files: `simple_feature.json` has the genome feature and `simple_func.json` has the functional annotation.

The content of the `src/nmdc/test_data/MetaG_annotation/simple_example.gff` file is:
   
```tab
Ga0185794_41	GeneMark.hmm-2 v1.05	CDS	48	1037	56.13	+	0	ID=Ga0185794_41_48_1037;translation_table=11;start_type=ATG;product=5-methylthioadenosine/S-adenosylhomocysteine deaminase;product_source=KO:K12960;cath_funfam=3.20.20.140;cog=COG0402;ko=KO:K12960;ec_number=EC:3.5.4.28,EC:3.5.4.31;pfam=PF01979;superfamily=51338,51556```
```


`simple_feature.json` looks like this:

```json
{
  "genome_feature_set": [
    {
      "seqid": "nmdc:Ga0185794_41",
      "start": 48,
      "end": 1037,
      "strand": "+",
      "type": "SO:0000316",
      "encodes": "nmdc:Ga0185794_41_48_1037"
    }
  ]
}
```

`simple_func.json` looks like this:
   
```json
{
  "functional_annotation_set": [
    {
      "subject": "nmdc:Ga0185794_41_48_1037",
      "has_function": "5-methylthioadenosine/S-adenosylhomocysteine deaminase",
      "was_generated_by": "nmdc:4ce9a799923b238585fc952135e5a0f5"
    },
    {
      "subject": "nmdc:Ga0185794_41_48_1037",
      "has_function": "CATH:3.20.20.140",
      "was_generated_by": "nmdc:4ce9a799923b238585fc952135e5a0f5"
    },
    {
      "subject": "nmdc:Ga0185794_41_48_1037",
      "has_function": "EGGNOG:COG0402",
      "was_generated_by": "nmdc:4ce9a799923b238585fc952135e5a0f5"
    },
    {
      "subject": "nmdc:Ga0185794_41_48_1037",
      "has_function": "KEGG.ORTHOLOGY:K12960",
      "was_generated_by": "nmdc:4ce9a799923b238585fc952135e5a0f5"
    },
    {
      "subject": "nmdc:Ga0185794_41_48_1037",
      "has_function": "EC:3.5.4.28",
      "was_generated_by": "nmdc:4ce9a799923b238585fc952135e5a0f5"
    },
    {
      "subject": "nmdc:Ga0185794_41_48_1037",
      "has_function": "PFAM:PF01979",
      "was_generated_by": "nmdc:4ce9a799923b238585fc952135e5a0f5"
    },
    {
      "subject": "nmdc:Ga0185794_41_48_1037",
      "has_function": "SUPFAM:51338",
      "was_generated_by": "nmdc:4ce9a799923b238585fc952135e5a0f5"
    }
  ]
}
```

