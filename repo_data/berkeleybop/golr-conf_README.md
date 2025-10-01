[![Build Status](https://travis-ci.org/berkeleybop/golr-conf.svg)](https://travis-ci.org/berkeleybop/golr-conf)

# golr-conf

## Overview

GOlr configuration handling and API.

Grossly put, the set of YAML files that define the possible search interfaces for GOlr are turned into JSON and fed as instantiating data into this API.

Currently, this is only really useful in the context of configuring a [bbop-manager-golr](https://github.com/berkeleybop/bbop-manager-golr) instance, or driving related GOlr widgetry.

This package contains three sub-packages:

* conf: the top-level configuration, it is a set of conf\_classes (including some meta-information; _roughly the set of all YAML files_
* conf\_class: a set of conf\_fields, including extra meta-information for displays and search boosts; _roughly equivalent to a single YAML file or a "personality"_
* conf\_field: a single entry, including information such as type, label, and tooltip text; _roughly equivalent to an entry in a YAML file_

The main current example of the conversion of the YAML source files to the JSON used for class instantiation is the blob used by the standard AmiGO GOlr configuration load. It easy to seen the similarities between the AmiGO 2 instance configuration [YAML files](https://github.com/geneontology/amigo/tree/master/metadata) and the [JSON output](http://amigo.geneontology.org/javascript/npm/amigo2-instance-data/lib/data/golr.js) used to drive the JavaScript interface.

(The YAML to JSON conversion has traditionally been done ad-hoc or with an old perl script, but we're currently looking at a direct YAML to JSON conversion for instantiation--feel free to drop us a line.)

For more detailed information, please see
the [unit tests](https://github.com/berkeleybop/golr-conf/tree/master/tests).

## Availability

[GitHub](https://github.com/berkeleybop/golr-conf)

[NPM](https://www.npmjs.com/package/golr-conf)

## API

[index](https://berkeleybop.github.io/golr-conf/doc/index.html)
