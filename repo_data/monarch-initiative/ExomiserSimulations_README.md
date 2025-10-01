# Exomiser simulations

This repo contains code for running simulations using Exomiser. The code usually receives one or more Phenopackets, simulate an exome and run the Exomiser analysis.

Simulated exome VCF file is being created in a naive way at the moment. A single VCF file with variants is required and the variants from `Phenopacket` are spiked in between the variants.

## Run *Lirical* simulations

You have to provide following arguments to run the code:

**Command line argumets:**
```bash
java -jar simulations-cli-0.2.1.jar 
--lirical 
--spring.config.location=/path/to/application.properties 
--pp=/path/to/phenopacket-dir 
--vcf=/path/to/template.vcf
```

- `--spring.config.location` should point to *application.properties* file with paths to Exomiser resources

## Run *3S*-related simulations

See the README file in the `plain-threes` module.
