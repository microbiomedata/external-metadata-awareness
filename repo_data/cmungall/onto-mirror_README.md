# onto-mirror

Allows for keeping a registry of locally checked out ontology
files. This is primarily useful if you want to work with versions of
ontologies in GitHub rather than those from the standard relase PURLs.

The file [void.ttl](void.ttl) contains triples that map an ontology
symbolic name to its location.

E.g.

```
<uberon> a void:Dataset ; void:dataDump <../uberon/uberon.owl> .
<uberon_ext> a void:Dataset ; void:dataDump <../uberon/ext.owl> .
<uberon_edit> a void:Dataset ; void:dataDump <../uberon/uberon_edit.owl> .
```

Note that local paths are used.

This assumes that you have ontologies checked out from github at the
same level as where you have this repo. E.g.

 * repos/
    * onto-mirror/
    * go-ontology
    * human-phenotype-ontology/

Any tool that respects the void standard could potentially use this. I
personally use this in conjunction with the SWI rdf library and [rdf_attach_library/1](https://www.swi-prolog.org/pldoc/doc_for?object=rdf_attach_library/1)

See below for instructions.

## use with SPARQLprog family of tools

See [sparqlprog](https://github.com/cmungall/sparqlprog)

Add to your `~/.profile`:

```
if [ -d $HOME/repos/onto-mirror/ ]; then
alias poq="pl2sparql -e -A $HOME/repos/onto-mirror/void.ttl -i"
fi
```

```
# query all label/2 (i.e. rdfs:label) in RO
poq ro label

# label match
poq uberon / lmatch limb _

# lexical search (see search_util)
poq uberon / lsearch limb _ -l
poq uberon / lsearch ^limb _ -l
poq uberon / lsearch limb$ _ -l

# viz
poq uberon / searchviz ^limb$
```


q command
```
poq uberon q ^limb$ l . s,part\ of viz
```
