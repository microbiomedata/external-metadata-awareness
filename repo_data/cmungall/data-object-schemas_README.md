![ga4gh logo](http://genomicsandhealth.org/files/logo_ga.png)

![travis status](https://travis-ci.org/david4096/data-object-schemas.svg?branch=develop)


Schemas for the Data Object Service (DOS) API
=============================================

This is used by the GA4GH Cloud Workstream

<img src="swagger_editor.png" width="48">[View in Swagger](http://editor2.swagger.io/#/?import=https://raw.githubusercontent.com/ga4gh/data-object-schemas/feature/protobuf-bdo-2/swagger/proto/data_objects_service.swagger.json)

The [Global Alliance for Genomics and Health](http://genomicsandhealth.org/) is an international
coalition, formed to enable the sharing of genomic and clinical data.

Cloud Workstream
----------------

The [Data Working Group](http://ga4gh.org/#/) concentrates on data representation, storage, and analysis, including working with platform development partners and industry leaders to develop standards that will facilitate interoperability. The Cloud Workstream is an informal, multi-vendor working group focused on standards for exchanging Docker-based tools and CWL/WDL workflows, execution of Docker-based tools and workflows on clouds, and abstract access to cloud object stores.

What is DOS?
------------

Currently, this is the home of the Data Object Service (DOS) API proposal. This repo has a CWL-based build process ready to go and a place for us to collectively work on [USECASES.md](USECASES.md).

This proposal for a DOS release is based on the schema work of Brian W. and others from OHSU along with work by UCSC.  It also is informed by existing object storage systems such as:

* GNOS: http://annaisystems.com/ (as used by PCAWG, see https://pcawg.icgc.org)
* ICGC Storage: as used to store data on S3, see https://github.com/icgc-dcc/dcc-storage and https://dcc.icgc.org/icgc-in-the-cloud/aws
* HCA Storage: see https://dss.staging.data.humancellatlas.org/ and https://github.com/HumanCellAtlas/data-store
* the GDC Storage: see https://gdc.cancer.gov
* Keep by Curoverse: see https://arvados.org/ and https://github.com/curoverse/arvados

The goal of DOS is to create a generic API on top of these and other projects, so workflow systems can access data in the same way regardless of project.  One section of the API focuses on how to read and write data objects to cloud environments and how to join them together as data bundles (Data object management).  Another focuses on the ability to find data objects across cloud environments and implementations of DOS (Data object queries).  The latter is likely to be worked on in conjunction with the GA4GH Discovery Workstream.

Key features of the current API proposal:

#### Data object management

This section of the API focuses on how to read and write data objects to cloud environments
and how to join them together as data bundles.  Data bundles are simply a flat collection
of one or more files.  This section of the API enables:

* create/update/delete a file
* create/update/delete a data bundle
* register UUIDs with these entities (an optionally track versions of each)
* generate signed URLs and/or cloud specific object storage paths and temporary credentials

#### Data object queries

A key feature of this API beyond creating/modifying/deletion files is the ability to
find data objects across cloud environments and implementations of DOS.  This
section of the API allows users to query by data bundle or file UUIDs which returns
information about where these data objects are available.  This response will
typically be used to find the same file or data bundle located across multiple
cloud environments.

Building Documents
------------------

Make sure you have Docker installed for your platform and the `cwltool`.

    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt

You can generate the [Swagger](http://swagger.io/) YAML from the Protocol Buffers:

    cwltool CWLFile

Find the output in `data_objects_service.swagger.json` and this can be loaded in the [Swagger editor](http://swagger.io/swagger-editor/).  Use the GitHub raw feature to generate a URL you can load.

When you're happy with the changes, checkin this file:

    mv data_objects_service.swagger.json swagger/proto/

And commit your changes, pushing to the appropriate branch.

How to contribute changes
-------------------------

Take cues for now from the [ga4gh/schemas](https://github.com/ga4gh/schemas/blob/master/CONTRIBUTING.rst) document.

License
-------

See the [LICENSE]

More Information
----------------

* [Global Alliance for Genomics and Health](http://genomicsandhealth.org)
* [Google Forum](https://groups.google.com/forum/#!forum/ga4gh-dwg-containers-workflows)


TODO/Questions
--------------
* do we want to use the [data bundles concept](https://docs.google.com/document/d/1d-9eu5X6ioOlqOJ9kkY8lHvXDF-KoynlmqJbuKVPMF0/edit#heading=h.b3jd47oqdd2e)? Often times we want to be able to model related files (like a workflow output) together in some way.  The data bundle concept supports this.
* do we want to support versioning (of files and data bundles)?  Implicit support right now in the sense that you can get an array of files or data bundles and use timestamp to understand their version.
* do all the timestamps need to be generated server-side?  This might be key for supporting versioning.
