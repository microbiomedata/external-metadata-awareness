## Synopsis

An experimental ontology metadata browser

## About

This is a browser for a registry of ontologies and ontology-like
artefacts. It is partially designed to replace the ancient OBO Library
interface on http://obofoundry.org - but should also be somewhat
generic

## Demo

Latest version may or may not be deployed on heroku

 * http://enigmatic-wildwood-5530.herokuapp.com/

Example page:

 * http://enigmatic-wildwood-5530.herokuapp.com/ontology/uberon

## Improvements over old page

 * doesn't suck
 * correctly models distinction between an ontology and the subsets/artefacts it produces
 * partial support for notion of sub-ontology, e.g. d-acts
 * supports various other metadata tags, including twitter feeds, publications, ...
 * social - integration with twitter
 * doesn't suck

## Repository metadata

The repository is stored as YAML in
[master/data/repository.yaml](data/repository.yaml). Technically
"YAML-LD" (it includes a JSON-LD @context. Only the subset of YAML
that is supported by JSON is used. This means it is formally a JSON-LD
file. And also formally an RDF file).

The application reads the YAML file. There is also a makefile provided
to "convert" the YAML-LD to RDF. This is an entirely generic
conversion, performed using JENA Riot (see Makefile):

 * [https://raw.githubusercontent.com/cmungall/omb/master/data/repository.ttl](data/repository.ttl)

## Metadata Datamodel

This is in flux, may change drastically. However, the aim is to
conform to void etc as much as possible.

The model is designed to support a distinction between ontologies in
the sense of an all-encompassing project (e.g. GO) and the different
editions of that ontology: e.g. subsets, supersets, bridge files.

## Local Installation

Check out the repo from github

``
npm install
``

Then

``
node app.js
``

After that connect to locahost:3000

## Redirects

One possibility is using the app as a replacement for OCLC. A demo has
been implemented with the Uerbon configuration, the YAML-LD looks like
this:

```
  - id: uberon
  ...
    redirects:
      - match: "releases/"
        url: "http://svn.code.sf.net/p/obo/svn/uberon/releases/"
      - match: ""
        url: "http://berkeleybop.org/ontologies/uberon/"
```

The idea is that http://purl.obolibrary.org/ could be mapped to the
deployed add. URLs starting with /obo/ are mapped to the redirects
above, in order (proxyPass may also be an option). E.g.


 * http://enigmatic-wildwood-5530.herokuapp.com/obo/uberon/bridge/uberon-bridge-to-nifstd.owl
 * http://enigmatic-wildwood-5530.herokuapp.com/obo/uberon/releases/2014-07-31/bridge/uberon-bridge-to-nifstd.owl


Class URIs automatically get redirected to OntoBee

 * http://enigmatic-wildwood-5530.herokuapp.com/obo/UBERON_0000955

It would be trivial to implemented overrides (e.g. for PR). TODO.



## TODO

 * separate registry from browser code
 * add some pizazz so it doesn't look like every bootstrap app out there
 * browsing of non-ontology artefacts (e.g. people)



