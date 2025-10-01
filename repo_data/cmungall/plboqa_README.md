## Synopsis

    :- ensure_loaded(prolog/boqa).
    :- ensure_loaded(prolog/boqa/rdfsboqa).
    
    :- use_module(library(semweb/rdf_db)).
    :- use_module(library(semweb/rdf_turtle)).
    
    query(Qs) :-
            bsearch(Qs,Item,P),
            format('P(~w | ~w) = ~w~n',[Item,Qs,P]),
            fail.
    query(_).
    
    t :-
            rdf_load('examples/data/mp-subset.ttl'),
            query(['reproductive system phenotype', 'abnormal cerebellum development', 'abnormal synaptic transmission']).
    

## About

This is an implementation of Bauer et al's Ontology Bayesian Search algorithm for ontologies: 
        
    @article{Bauer2012,
        title = {{Bayesian ontology querying for accurate and noise-tolerant semantic searches.}},
        abstract = {Ontologies provide a structured representation of the concepts of a domain of knowledge as well as the relations between them. Attribute ontologies are used to describe the characteristics of the items of a domain, such as the functions of proteins or the signs and symptoms of disease, which opens the possibility of searching a database of items for the best match to a list of observed or desired attributes. However, naive search methods do not perform well on realistic data because of noise in the data, imprecision in typical queries and because individual items may not display all attributes of the category they belong to.},
        author = {Bauer, Sebastian and K\"{o}hler, Sebastian and Schulz, Marcel H and Robinson, Peter N},
        doi = {10.1093/bioinformatics/bts471},
        issn = {1367-4811},
        journal = {Bioinformatics (Oxford, England)},
        month = Oct,
        number = {19},
        pages = {2502--8},
        pmid = {22843981},
        url = {http://www.ncbi.nlm.nih.gov/pubmed/22843981},
        volume = {28},
        year = {2012}
    }

Original implementation:

 * http://compbio.charite.de/contao/index.php/boqa.html


The implementation is designed to be pluggable with respect to how
underlying prolog data maps to the BN. However, at the moment there is
only one plugin, rdfsboqa, which implements a simple RDF Schema map
using the SWI semweb library:

 * Terms (e.g. Phenotypes) are OWL classes
 * Items (Diseases) are instances (rdf:type) of OWL classes
 * The inference rule is the reflexive transitive closure of rdfs:subClassOf (i.e. rdfs_subclass_of/2)

## Worked Example

This example uses the famous pizza ontology. The goal here is to
'diagnose' a pizza based on a possibly unreliable list of observed
topping. See the file examples/boqa_pizza.pl for the source (the pizza
ontology is included in ttl format in this distribution).

This example makes use of the SWI semweb library to generate the
network topology from the pizza, so we will need to include the
relevant modules. We also take the opportunity to declare a namespace
for convenience:

```
:- use_module(library(semweb/rdf_db)).
:- use_module(library(semweb/rdfs)).

:- rdf_register_ns(pizza,'http://www.co-ode.org/ontologies/pizza/pizza.owl#').
```

Because we are providing our own hooks we need to declare these - more on this later:

```
:- multifile boqa:class_ancestor/2.
:- multifile boqa:inferred_association/2.
:- multifile boqa:cls/1.
:- multifile boqa:item/1.
```

First we need to declare how to enumerate the 'items' we are
classifying. We declare a convenience unary predicate pizza/1 that
unifies with the URI of a subclass of pizza:

```
boqa:item(X) :- pizza(X).
pizza(X) :- rdfs_subclass_of(X,pizza:'Pizza').
```

Note that rdfs_subclass_of/2 uses RDFS entailment, so we get the
reflexive closure over rdfs:subClassOf

Next we declare how to enumerate over all classes (terms) in the ontology:

```
boqa:cls(X) :- rdf(X,rdf:type,owl:'Class').
```

Optionally we can override the defaults here:

```
boqa:p_false_negative(_,0.05).   % chance we fail to observe a topping
boqa:p_false_positive(_,0.05).   % chance we mistakenly imagine a topping to be there
```

The tricky part here is declaring how to find (reflexive) ancestors of
a class. We are using an OWL ontology with an RDFS library here, so
this is a bit low-level. It's also incomplete - for now we satisfy
ourselves with traversing the subclass hierarchy, possibly hopping
over a single existential axiom (e.g. X hasTopping some Y):

```
boqa:class_ancestor(X,Y) :- rdfs_subclass_of(X,Y), \+ rdf_is_bnode(Y).
boqa:class_ancestor(X,Y) :-
        rdfs_subclass_of(X,Z),
        % ignore edge labels
        rdf(Z,owl:someValuesFrom,W),
        rdfs_subclass_of(W,Y),
        \+ rdf_is_bnode(Y).
```

For convenience we provide lookup/2 which allows us to use the URI
fragment (e.g. NeopolitanPizza) to refer to a class rather than the full URI:

```
boqa:lookup(L,U) :-
        rdf_global_id(pizza:L,U),
        !.
```

That's it!

We can now query using a list of query terms:

```
bsearch(['GreenPepperTopping', 'HotSpicedBeefTopping', 'OnionTopping'],Item,Pr).
```

This should give the top hit of SloppyGuiseppe

## TODO

 * Frequency-augmented network
 


