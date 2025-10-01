## Monarch System Installer

This package contains the components required to run the Monarch
System locally. This allows you to extend the dataset used by OWLSim
to include private/local phenotype data.

For a system diagram, see the docs/ directory

## Installation

Two servers need to be installed

1. An OWLSim analysis and phenotype matching server
2. The Monarch REST API

Both run as embedded Jetty.

### Setting PATH

You need one executable on your path for the preparation and server
startup. Assuming you unpacked this distribution in your home
directory, type

    export PATH="$PATH:~/monarch-installer/owltools/OWLTools-Runner/bin/owltools"



### Running OWLSim

First you need to prepare the input files. From this directory, type:

    make prepare-owlsim

Note: if you wish to add custom data, see the notes below

Preparation can take over an hour dependending on dataset size, as
large caches are prepared. This step does not need to be rerun until
the data changes again.

Once this step is complete, start the server:

    cd phenotype-ontologyes/server
    ./start-owlsim-server.sh

By default the server will be on port 9000 (this can be custiomized)

### Running Monarch Services

    cd monarch-app
    ./start-server-production.sh

This starts a server on port 8080

Note: you may need to customize this file:

 * monarch-app/conf/server_config_production.json 

Change the following line:

    "owlsim_services_url" : "http://owlsim.monarchinitiative.org/",

To:

    "owlsim_services_url" : "http://127.0.0.1:9000/",

(assuming both servers are running on the same machine)

TODO: make this part automatic

## Customized datasets

Add your own phenotype associations here:

 * phenotype-ontologies/server/additional-associations.txt 

See the example file for formatting instructions

After this is done, run "make prepare-owlsim" from this directory

## Building this installer

Note: if you obtained this from github, then you will have to build
the installer using the Makefile
