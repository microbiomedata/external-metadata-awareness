[![Build Status](https://travis-ci.org/berkeleybop/bbop-manager-golr.svg)](https://travis-ci.org/berkeleybop/bbop-manager-golr)

# bbop-manager-golr

## Overview

This package is a system for coherently and abstractly managing
communication (callbacks, promises, etc.) with GOlr instances (Solr
servers with a structured schema).

To see how this all works in practice, maybe start with the
[quickstart guide](#quickstart).

The bbop-mananger-golr is an object and API for making queries to, and
getting responses from, a GOlr server. The API allows you to: change
the parameters, add and remove query fields, operate on facets, and
search terms of the query; to make multiple queries; and to handle
different types of responses in different ways. Using this
abstraction, you can use almost identical code on the client or
server, or using promise or callback styles.

By way of introduction, the constructor takes four arguments:

* the target GOlr URL
* a JSON-ified YAML configuration object (see [golr-conf](https://github.com/berkeleybop/golr-conf))
* the "engine" type (jquery, node)
* _optional_ mode (asynchronous or synchronous, not always available)

If using the callback mode, users can also "register" functions to run
in various pre-set orders against various internal events, such as
"prerun", "search", and "error".

The non-error return type of manager calls is a [bbop-response-golr](https://github.com/berkeleybop/bbop-response-golr).

This is a subclass of [bbop-rest-manager](https://github.com/berkeleybop/bbop-rest-manager). The suggested reading list for understanding this package, in order, is:

* [bbop-rest-manager](https://github.com/berkeleybop/bbop-rest-manager) (superclass of bbop-manager-golr)
* [bbop-rest-response](https://github.com/berkeleybop/bbop-rest-response) (superclass of bbop-reponse-golr)
* [golr-conf](https://github.com/berkeleybop/golr-conf) (configuration for bbop-manager-golr)
* this document (subclass of bbop-rest-manager)
* [bbop-response-golr](https://github.com/berkeleybop/bbop-response-golr) (subclass of bbop-rest-response)

For more detailed information, please see
the [unit tests](https://github.com/berkeleybop/bbop-manager-golr/tree/master/tests).

## Quickstart

To see how this all hangs together, lets start with the concrete
example of using the library with the AmiGO public data for the Gene
Ontology. We're going to assume that we're going to use a standard
Node.js environment, using promises (although we could use synchronous
or callbacks just as easily).

The complete, working, and commented example can be found [here](https://github.com/geneontology/amigo/blob/master/scripts/amigo-data-demo-02.js).

### Instance data

First, we need to get our instance data together. This is similar to
getting location and schema information when dealing with a RDMS. Fortunately, AmiGO provides a package for this on NPM:

```javascript
var amigo = new (require('amigo2-instance-data'))();
var golr_conf = require('golr-conf');
var gconf = new golr_conf.conf(amigo.data.golr);
var gserv = amigo.data.server.golr_base; // just a URL string
```

This gives us the location (gserv) and schema info (gconf).

Next, let's setup the manager, using the Node.js engine, and the response class that we want to handle/wrap any response that we get from the server.

```javascript
var impl_engine = require('bbop-rest-manager').node;
var golr_manager = require('bbop-manager-golr');
var golr_response = require('bbop-response-golr');

var engine = new impl_engine(golr_response);
var manager = new golr_manager(gserv, gconf, engine, 'async');
```

We now have a manager that: 1) is aiming at the location defined by
_gserv_, 2) is configured with the "schema" in _gconf_, 3) will use
_engine_ to make contact, which in turn will make use of
_golr\_response_ as the response type, and 4) will be asynchronous
(optional/superfluous option in most cases).

Now let's make use of what we have. How about a project and get all
PMIDs for experimental human annotations to "neuron development". I
happen to know what "schema" I'm working against, but for those
unfamiliar with AmiGO, you can get an idea from
[here](http://amigo.geneontology.org/amigo/schema_details).

Let's tell the system that we only want annotation docs, and that we
want only our specific subset.

```javascript
manager.set_personality('annotation');
manager.add_query_filter('document_category', 'annotation', ['*']);

manager.add_query_filter('regulates_closure', 'GO:0048666');
manager.add_query_filter('taxon_subset_closure', 'NCBITaxon:9606');
manager.add_query_filter('evidence_subset_closure', 'ECO:0000006');
```

Finally, let's trigger the search, get the promise, and look at our
results.

```javascript
var promise = manager.search();
promise.then(function(resp){

    // Process our response instance using bbop-response-golr.
    if( resp.success() ){
        us.each(resp.documents(), function(doc){

            // Slightly contrived use if resp.get_doc_field().
            var id = doc['id'];
            var refs = resp.get_doc_field(id, 'reference');
            console.log(refs.join("\n"));
        });
    }
});
```

There are many other example in the tests directory, as well as many
practical examples in the AmiGO 2 repository, including a well
documented
[REST API](https://github.com/geneontology/amigo/blob/master/bin/amigo.js)
built up with this abstraction.

## Documentation

This is a very recent port to a new set of modern managers (able to be
used in Node and the browser, in both synchronous and asynchronous
modes). While the initializations are a little different (please see
the unit tests), the API is pretty much the same. Until we can update
the documentation, please see the API docs of the pre-port version
[here](https://github.com/berkeleybop/bbop-js).

## Availability

[GitHub](https://github.com/berkeleybop/bbop-manager-golr)

[NPM](https://www.npmjs.com/package/bbop-manager-golr)

## API

[index](https://berkeleybop.github.io/bbop-manager-golr/doc/index.html)
