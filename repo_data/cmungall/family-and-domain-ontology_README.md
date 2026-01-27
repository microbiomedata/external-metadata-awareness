# Protein Domain Ontology

A hybrid automatically constructed ontology of protein domains and
proteins classified by structural families.

See:

 * domo.obo

Example:

 / IPR:000000 ! domain
  is_a IPR:000217 ! Tubulin
   po IPR:002452 ! Alpha tubulin *** 
   po IPR:002453 ! Beta tubulin *** 
   po IPR:002454 ! Gamma tubulin *** 
   po IPR:002967 ! Delta tubulin *** 
   po IPR:004057 ! Epsilon tubulin *** 
   po IPR:004058 ! Zeta tubulin *** 
  is_a IPR:007259 ! Spc97/Spc98
   is_a IPR:015697 ! Gamma tubulin complex protein 3 *** 

Note that some classes have IDs "IPRGO" - these are domain-binding
proteins for which we can not find an IPR ID, so we generate a class
and place it in the hierarchy under domain - or if we can use Marijn's
mapping we do.

Example:

  is_a IPR:000000 ! domain
   is_a IPR:011029 ! Death-like domain
    is_a IPR:000488 ! death domain
     is_a IPRGO:0051434 ! BH3 domain *** 
   is_a IPRGO:0051400 ! BH domain
    is_a IPR:003093 ! BH4 domain
    is_a IPRGO:0051432 ! BH1 domain
    is_a IPRGO:0051433 ! BH2 domain
    is_a IPRGO:0051434 ! BH3 domain *** 

# domains vs families

Interpro contains domains and families.

We expect the domains to fall under 'protein domain specific binding'
in GO

Families just fall under 'protein binding'

  is_a GO:0005488 ! binding
   is_a GO:0005515 ! protein binding
    is_a GO:0071253 ! connexin binding 

Which corresponds to

   is_a IPR:000500 ! connexin *** 
    is_a IPR:002260 ! Gap junction delta-2 protein (Cx36)
    is_a IPR:002261 ! Gap junction alpha-1 protein (Cx43)
    is_a IPR:002262 ! Gap junction alpha-3 protein (Cx46)
    is_a IPR:002263 ! Gap junction alpha-4 protein (Cx37)
    is_a IPR:002264 ! Gap junction alpha-5 protein (Cx40)
    is_a IPR:002265 ! Gap junction alpha-6 protein (Cx45)
    is_a IPR:002266 ! Gap junction alpha-8 protein (Cx50)
    is_a IPR:002267 ! Gap junction beta-1 protein (Cx32)
    is_a IPR:002268 ! Gap junction beta-2 protein (Cx26)
    is_a IPR:002269 ! Gap junction beta-3 protein (Cx31)
    is_a IPR:002270 ! Gap junction beta-4 protein (Cx31.1)
    is_a IPR:002271 ! Gap junction beta-5 protein (Cx30.3)

Where no IPR exists we can get the assumed hierarchy from GO, e.g.

   is_a IPRGO:0019899 ! enzyme
    is_a IPRGO:0070063 ! RNA polymerase
     is_a IPRGO:0043175 ! RNA polymerase core enzyme
      is_a IPRGO:0000993 ! RNA polymerase II core *** 
      is_a IPRGO:0000994 ! RNA polymerase III core *** 
      is_a IPRGO:0001042 ! RNA polymerase I core *** 
      is_a IPRGO:0001048 ! RNA polymerase IV core *** 
      is_a IPRGO:0001049 ! RNA polymerase V core *** 

Note that this seems to fall into PRO's territory. However, the PRO
hierarchy is currently quite flat

E.g.

     is_a PR:000000001 ! protein
      is_a PR:000007991 ! gap junction alpha-10 protein *** 


# Logical Definitions for GO

Logical definitions for protein binding terms

 * x-domain.obo

Available for browsing in a merged file:

binding subset of GO plus logical defs plus domo

 * merged.{obo,owl}


See example-tubulin.png


///

What do we do about:

 / GO:0003674 ! molecular_function
  is_a GO:0005488 ! binding
   is_a GO:0005515 ! protein binding
    is_a GO:0001948 ! glycoprotein binding
     is_a GO:0043394 ! proteoglycan binding
      is_a GO:0035373 ! chondroitin sulfate proteoglycan binding *** 
   is_a GO:0043167 ! ion binding
    is_a GO:0043168 ! anion binding
     is_a GO:0035373 ! chondroitin sulfate proteoglycan binding *** 
   is_a GO:0097367 ! carbohydrate derivative binding
    is_a GO:0005539 ! glycosaminoglycan binding
     is_a GO:0035373 ! chondroitin sulfate proteoglycan binding *** 
   is_a GO:1901681 ! sulfur compound binding
    is_a GO:0035373 ! chondroitin sulfate proteoglycan binding *** 

should go in PRO?

///

# TODOs

## Matching

We currently have no automatic way of matching

    [Term]
    id: GO:1990175
    name: EH domain binding
    def: "Interacting selectively and non-covalently with an EH domain of a protein. The EH stand for Eps15 homology. This was originally identified as a motif present in three copies at the NH2-termini of Eps15 and of the related molecule Eps15R." [GOC:hjd, PMID:11911876, PMID:21115825]
    is_a: GO:0019904  ! protein domain specific binding

to

http://www.ebi.ac.uk/interpro/entry/IPR000261
EPS15_homology|EPS15 homology (EH)

How is this best curated?

use info in parentheses?

## 


# Pipeline

See Makefile for more details.

## Translate interpro to OBO

We use the interpro.xml file and the ParentChildTreeFile.txt to make 

 - ipr-core.obo
 - ipr-names.obo

All have IDs IPR:nnnnnn

## GO Binding terms to Interpro

Input: interpro_binding_edited.txt

(this is an edited version of Martijn's file)

This makes iprgo-core.obo

## Deriving info from GO

We want to make use of the implicit ontology in GO to mine textual definitions

The script go2ipr extracts this from the relevant subset of GO

The IDs are all of the form IPRGO:nnnn (where the fragment matches the
GO binding class ID fragment).

## Merging

We need to merge the interpro-derived and the GO-derived files

We first make a set of equivalence axioms using lexical entity matching.

We then use owltools to merge these together
