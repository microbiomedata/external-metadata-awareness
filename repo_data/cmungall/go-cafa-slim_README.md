# GO CAFA slim

This is intended as an exploration point for a GO slim that could be used for meaningful function prediction benchmarking. The idea is to filter out terms

- that are too broad to be useful
- that are too specific

It is NOT based on IC metrics. The goal is to do this based on biologically and ontologically meaningful criteria. As a starting point we are using the IBA
subset pulled from amigo. See the Makefile for details.

Currently we set the threshold to 1; i.e a term needs only used ONCE in IBA for it to be included.

The end result is too big, but is intended as a conversational starting point.

We use [ROBOT extract](https://robot.obolibrary.org/extract#subset) with the relation-graph subset method that performs gap filling;

i.e. given

* A is-a B part-of C

If slim=`{A,C}` then the ontology will have `A part-of C` as the reasoned most direct link.

obo file here:

[https://github.com/cmungall/go-cafa-slim/blob/main/subset/iba-slim.obo](https://github.com/cmungall/go-cafa-slim/blob/main/subset/iba-slim.obo)

browsable here:
https://bioportal.bioontology.org/ontologies/GO-CAFA-SLIM?p=classes

## TODO

- identify why some very high level terms are here
   - host
   - catalytic activity
   - nucleic acid binding

We can explore some of these in amigo by doing direct filters, e.g.
 
<img width="1646" alt="image" src="https://github.com/user-attachments/assets/d830c59a-dfec-41c8-b87e-c3199d969192" />







