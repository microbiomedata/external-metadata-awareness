# Carnival-Penn

Carnival-Penn is a collection of modules and applications built using the [Carnival](https://github.com/pmbb-ibi/carnival) framework.


<a name="getting-started"></a>
## Getting Started
See [PMBB/TURBO CLI Quick Start](app/carnival-pmbb/README.md#quickstart) for getting started with the PMBB command line interface.

See [Prototype Cohort Explorer Microservices Guide](app/carnival-explorer-server/readme.md) for instructions on running the cohort explorer application with docker.

See [developer setup](docs/developer-setup.md) for full documentation on how to set up a development environment.

<a name="modules"></a>
## Module Overview
| module | description |
| --- | --- |
| [carnival-pennmedicine](app/carnival-pennmedicine/README.md) | The carnival-pennmedicine module contains services that cross-cut Penn Medicine, such as Penn Data Store vines to pull diagnoses and medication prescriptions. |
| [carnival-pmbb](app/carnival-pmbb/README.md) | The carnival-pmbb module contains services specific to the Penn Medicine Biobank, such as Pumpkin and SPS vines to query for specimens. It also contains the PMBB-Carnival command line interface application. |
| [carnival-pop](app/carnival-pop/README.md) | carnival-pop is a project module for the Prescription Opioid Project sponsored by Drs. Caryn Lerman and Justin Beckelman. |
| [carnival-turbo](app/carnival-turbo/README.md) | carnival-turbo is the intersection of Carnival and the TURBO-* suite of applications that support biomedical research through ontologies and knowledge bases. |
| [carnival-explorer-server](app/carnival-explorer-server/readme.md) | The carnival-explorer-server module is the micronaut server for the prototype Cohort Explorer application. |
| [carnival-explorer-client](app/carnival-explorer-client/README.md) | The carnival-explorer-client module is a react web client for the prototype Cohort Explorer application.  It is intended to be a simple example service that can be replaced with a different web client. |

The base carnival module overview is [here](https://github.com/pmbb-ibi/carnival#package-overview).

<a name="installations"></a>
## Installations
Carnival-PMBB is installed on [willow.pmacs.upenn.edu](docs/willow.md).  The documentation includes installation instructions.

<a name="reference"></a>
## Graph Schema Reference(incomplete)
* carnival-pennmedicine
  - [Schema](https://github.com/pennbiobank/carnival-penn/blob/master/app/carnival-pennmedicine/src/main/groovy/carnival/pennmedicine/graph/PennMedicine.groovy)
  - [Graph/Controlled Instances](https://github.com/pennbiobank/carnival-penn/blob/master/app/carnival-pennmedicine/src/main/groovy/carnival/pennmedicine/graph/PennMedicineGraph.groovy)
  
## Reference Links

* [Prototype Cohort Explorer Microservices Guide](app/carnival-explorer-server/readme.md) - Instructions for building and running the prototype cohort explorer application
* [PMBB/TURBO CLI Quick Start](app/carnival-pmbb/README.md#quickstart) - Instructions for building and running the PMBB CLI application
* [Developer Guide](docs/developer-setup.md) - Developer environment setup and instructions for developing Carnival modules and applications
* [Github Pages Website](https://pmbb-ibi.github.io/carnival/)
* [legacy scripts](app/carnival-core/doc/legacy-issues.md)
* [Base carnival graph specification(deprecated; see code impelentations)](https://github.com/pmbb-ibi/carnival/blob/master/app/carnival-core/doc/graph.md)



