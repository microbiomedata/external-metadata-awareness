[![DOI](https://zenodo.org/badge/13996/cmungall/reactioner.svg)](https://zenodo.org/badge/latestdoi/13996/cmungall/reactioner)

# reactioner (ALPHA RELEASE)

Parses textual descriptions of reactions into pathways and OWL expressions


## Installation

(NOTE: we will soon have docker which will be easier)

Install SWI-Prolog from http://www.swi-prolog.org

Run directly using [bin/reactioner](bin/reactioner)

## Reports

 * [data/go-rhea-newsyns.tsv](data/go-rhea-newsyns.tsv) - suggested syns from RHEA
 * [data/go-rhea-check.tsv](data/go-rhea-check.tsv) - checking RHEA xrefs

## Algorithm

This code parses structured text definitions of reactions (in particular, those used by GO).

For example, the def for [sucrose synthase activity](http://purl.obolibrary.org/obo/GO_0016157) is

_Catalysis of the reaction: UDP-glucose + D-fructose = UDP + sucrose._

We employ a 3-step Parse-Match-Balance on each. After this we translate the expression to an OWL expression.

### Step 1: Parse

The reaction string is parsed according to a grammar:

```
Reaction ::= Participant[ + Participant]* = Participant[ + Participant]*
```

The grammar is encoded by a prolog DCG. The grammar is semi-deterministic, so each string has zero or one parses

TODO: co-efficients/stoichiometry

See also:
Jupe et al. (https://doi.org/10.1093/database/bau060)

for generative approach in Reactome

### Entity Matching

Each of the participants is matched using CHEBI. Because strings do
not uniquely and unambiguously identify a chemical entity, we produce
all combinations of possible reactions. We score each reaction
according to the strengths of each match.

We prioritize matches to name/label above synonym matches. We treat
all synonym scopes as equivalent, as CHEBI uses related vs exact
arbitrarily.

TODO: use rhea-suggested synonyms

### Balancing

We prioritize balanced reactions above unbalanced ones, or ones in
which balance can not be determined. The assumption is that false
CHEBI matches will be less likely to balance.

A subset of CHEBI classes have a property `chebi:formula` that maps to
a string such as `C15H24N2O17P2`. We use this to count the number of
each element on each side. A penalty is introduced for every
unabalanced element.

For example:

_Catalysis of the reaction: UDP-glucose + D-fructose = UDP + sucrose._

Parses and matches to the prolog term:

```

['http://purl.obolibrary.org/obo/CHEBI_18066'/'UDP-D-glucose',
 'http://purl.obolibrary.org/obo/CHEBI_15824'/'D-fructose'] =
['http://purl.obolibrary.org/obo/CHEBI_58223'/'UDP(3-)',
 'http://purl.obolibrary.org/obo/CHEBI_17992'/sucrose],21,['N'-0,'P'-0,'C'-0,'H'- -3,'O'-0]).
```

(note the above is an actual prolog term, the predicate `=` is written in infix form

### Learning of grouping classes

Goal is to infer definitions of grouping classes

For any grouping class C, we take all asserted ancestors, and determine the reaction for each one.

We want to compare this against all other reactions.

We treated this as a standard classification problem and use tree
learning in scikit-learn, where the features/predictors are properties
of the reaction and the target is a binary variable for member of
class / not member

Each reaction is decomposed to chemical entities to derive base
features, and then these generate features for the overall reaction of
the form

<SIDE>_<NUMBER>_<BaseFeature>

The BaseFeature is derived from the CHEBI class

### Conversion to OWL (TODO)

We use the "Ygevny transform" by default.

### Logical Match to RHEA (TODO)

Exact match can be performed. For true equivalence or subsumption test use an OWL reasoner.

### Deriving synonyms from RHEA

Often RHEA will use a CHEBI ID that does not seem justified by the label they use.

We can query their RDF, RHEA uses their own labels for each compound,
and map this to CHEBI. We can query these pairs:

 * [data/go-rhea-newsyns.tsv](data/go-rhea-newsyns.tsv) - suggested syns from RHEA

We note whether the label they choose is a new string or corresponds to a different ID (ambiguous)

### Semantic Similarity search of RHEA, MetaCyc etc

We don't always expect exact matches.

We can do standard semantic similarity matching, using CHEBI
graph. However, we may want to pull in other features of chemical
entities rather than rely on pre-asserted hierarchy.

Chym See:
https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000937
