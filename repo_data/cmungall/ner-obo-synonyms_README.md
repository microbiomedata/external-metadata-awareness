# Effect of OBO synonym scopes on Named Entity Recognition

How does the strategy of omitting BROAD/NARROW/RELATED synonyms affect precision/recall/accuracy/F1?

See the Makefile to repeat the analysis

See summary-*.txt for summary statistics

Strategies:

 * all: use all synonym scopes (and primary names)
 * exact: only use EXACT and the primary name
 * exrel: omit BROAD/NARROW

## Background

 * https://github.com/obophenotype/uberon/wiki/Using-uberon-for-text-mining
 * http://owlcollab.github.io/oboformat/doc/obo-syntax.html#5.8.1
