
This is a draft of a treatment of modal-style operators (e.g. "might",
"typically") in OWL.

It is intended to give a treatment of existing relations such as
"capable of" and provide a way of linking these pseudo-class-level
relations to observable non-qualified instance-level relations.

The goal is to have a practical set of axioms and axiom
transformations that can be used for query-answering rather than a
philosophical treatment.

THIS IS AN EARLY DRAFT. It combines some practical approaches with
more radical suggestions, these portions may be split out in future.

## Background

Consider the following statements:

 * every sperm cell fises with an egg cell
 * every Shh protein is involved in heart development
 * every british car drives on the left
 * everyone must obey the law
 * every heart pumps blood
 * every mouse has a tail
 * every aspirin treats a headache

Every statement is false, as there exist numerous exceptions, with
sometimes exceptions being in the majority.

However, it seems there is some kind of genuine, useful, queryable
relationship between the class on the left and the class on the
right. How do we capture this?

One way to do this is to attach an operator to each
sentence. Informally, we can draft a list of modal linguistic
operators, ordered roughly in terms of strength:

 * sometimes
 * may
 * typically
 * is designed to
 * has evolved to
 * is obliged to
 * is capable of
 * is known to
 * necessarily, except under rare circumstances

We can use the linguistic qualifiers to name a series of
relationships, such as "may participate in" (see for example, the NCI
Thesaurus). This is slightly unsatisfying. How do these qualified
relations relate to their unqualified counterparts? When should the
qualified versions be used over the unqualified ones? When do these
become weak to the point of uselessness? This is important for
developing and querying over knowledge bases in a consistent manner.

These operators can be viewed as *modal* operators. Modal logic
provides a system for operating on these operators (typically
"necessity" and "possibility"). However, modal logic may introduce
additional commitments and machinery, and in any case OWL does not
support modal logic.  How do we go about encoding our qualifiers in
OWL?

(Discussion of Shulze et al paper on ELF1 here)

(Need more details on why modal logic slightly different - "competes"
with OWL subClassOf relations?)

## OWL Pattern

For every modal qualifier in our domain, we create a modal operator
object property. Call this set of properties M = m1, m2, ... (we will
return later to the implications of treating the operator as an object
property).

We also have a set of unqualified "pure" object properties in our
domain. Call this set P = p1, p2, ...

We can name any qualified propert _mp_ from the cross product MP = M x
P.

For any _mp_ in MP, we add an axiom:

    mp <- m *o* p

This has the side effect of inheriting a _safe_ set of characteristics
from p. For example, if p is transitive, then _mp_ will hold for any
chain x1 m x2 p x3 p x4 ... p xn. However, other characteristics such
as symmetry or functional will *not* carry over.

Note that in OWL we cannot state the reciprocal, i.e. mp -> m *o* p,
however, we could define a macro mp <-> m *o* p, such that an
existential is introduced when going in the reverse direction.

We further distinguish a subset M^s of M. These are the set of
*reflexive* or self-modal operators. If m is in M^s then mp implies p,
i.e.
  
    for all mp in MP, m in M^s, p in P, add:
      mp <- p

We are are working in an expressive enough variant of OWL, we can add

    for all m in M^s, add: Reflexive(m)

Or

    for all m in M^s, add: C SubClassOf M self

For some appropriately high-level C

The decision as to which operators to place in M^s is domain-specific,
with the exception of operators such as "some" or "possibly", if it is
already included in M. Intuitively, if a relation holds, for some pair
then there is some pair for which it holds, and it is possible for
that relation to hold.

In practical terms, the self-modal operators make lattice-like
subproperty hierarchies. E.g. given a base property like "part of" and
a base subproperty like "boundary part of":

       may be part of
      /             \
    part of    may be boundary part of
      \             /
      boundary part of

## Insulation characteristics

One of the main desirable characteristics of applying an operator is
to insulate from exceptions. For example, the following yields no
contradiction:

    Shh SubClassOf typically-involved-in some Heart-Development
    ssh0001 Type Shh
    not(ssh0001 involved-in some Heart-Development)

Furthermore, exception-like structures can easily be queried, e.g. in
the ABox:

    SELECT * WHERE
     { ?i Type typically-R some ?X . NOT(?i Type R some ?X) }

## Models and use of existential quantification

Treating operators as object properties has implications for the
models implied by our ontologies and knowledge bases.

For example, given a TBox axiom:

    mouse SubClassOf typically-has-part some tail

And

    mouse1 Type Mouse

Assuming the bidirectional implication for object properties in MP,
there is a model:

    mouse1 typically x
    x has-part t
    t Type tail

We call this the existential-restriction-modal-chain (ERMC) pattern,
as we are saying there exists some x where x is in the modal relation
to mouse1.

This poses the question: what is x? What is the actual relationship to
mouse1? The domain modeler may choose to simply ignore this question
and treat x as an artifact of formalization of typicality in
OWL. Alternatively, the domain modeler may choose to give an account
in a number of different ways, perhaps invoking possible-worlds, or a
real evolutionary ancestor. Or we may choose to use a modal operator
such as "similar to". See further on in this document.

One possibility is to treat _x_ as some kind of dispositional
entity. We can introduce a new relation that connects a disposition to
a situation in which it comes about (say "materialized-by"). This
affords us the possibility of using a universal quantifier, e.g.

    mouse1 typically x
    x materialized-as ONLY (has-part some Tail)

We call this the universal-restriction-dispositional-entity (URDE)
pattern.

Aside: Note that URDE can be seen as a generalization of BFO
dispositions (which are realized by processes). We could perhaps use
BFO dispostions if we are allowed some kind of process-IC relation
such as "being", such that any state-of-affairs could be encoded by a
being-process.

URDE may be viewed by some as philosophically preferable by some on
the grounds of parsimony and realism: it does not introduce any new
physical entities, imagined or otherwise. However, one could still
question the introduction of a new "real"-but-invisible dispositional
entity _x_ (if one wanted to go down that rabbit hole). It may be the
case that EMC is the more philosophically defensible of the two (if
this matters to us).

From a computational perspective it is not clear that this URDE
pattern offers any advantages over the EMC pattern. In fact it is
arguably worse, as it forces us to step outside EL++, and it
introduces other difficulties (difficulties of property chaining).

## Domain-specific application

One of the primary use cases is in molecular biology, where we wish to
make statements of genes and gene products in general, but must be
wary of being too strong.

E.g. intuitively we may say

    Shh-protein involved-in Heart-development

But there may be many instances of Shh-protein that do not.

Similarly, at a cellular level:

    photoreceptor cell involved-in detection-of-light-stimulus

But this may not always be true. This poses genuine practical problems
if we are to make use of stromg disjointness axioms in our ontology
that will be overridden by real-world situations.

The capable_of and capable_of_part_of relations were introduced to
deal with this. These were conceived as shortcuts, e.g.:

    photoreceptor cell SubClassOf capable_of some detection-of-light-stimulus
    ==>
    photoreceptor cell SubClassOf bearer-of some (realized-by only detection-of-light-stimulus)

Or, using the GCI interpretation    

    photoreceptor cell SubClassOf capable_of some detection-of-light-stimulus
    +
    capable_of some detection-of-light-stimulus SubClassOf bearer-of some (realized-by only detection-of-light-stimulus)

In practice, the expansion step has not been required for useful
reasoning. Note that this only works for processes (although see above
for a generalization).

An alternate formalism is to treat capable_of as the modal form of
some base relation, e.g. "executes", "agent in" or "enables", that
holds between a material entity and a process that is actively being
carried out by that material entity. i.e.

    capable_of <-> prototypically *o* enables

Note that OWL cannot express "<->" here we treat this as an axiom
replacement operation prior to reasoning.

Thus under this definition it is valid to transform:

    photoreceptor cell SubClassOf capable_of some detection-of-light-stimulus

To:

    photoreceptor cell SubClassOf prototypically some (enables some detection-of-light-stimulus)

From a terminological perspective it may be preferable to name the
modal property "has prototype". Although we still have not addressed
the question of what it means to be a prototype, and whether the
prototypical individual has a real-world interpretation, or is some
artifact present in the model but to be ignored.

There are a variety of options here. One is to invoke possible-worlds
semantics, which has the advantage of aligning well with treatments of
modal logics (note that this does not entail any kind of many-world
interpretation in the "real world").

However, this may not be necessary. We can argue that the prototype
exists in this world - possibly in the past (for example, a strong
evolutionary interpretation would be to place the prototype as the
ancestor). This real-existing-prototype has only properties that
we could expect to see propagated in the modal form.

The counter-argument is that there are arguably cases where no such
prototypical entity exists. For example, our prototype photoreceptor
may have the property of being part of a vermiform animal. But we may
not wish to say that photoreceptors prototypically are part of worms.

### Co-existence of interpretations

For process-prototypes there is no reason why EMC and URDE
interpretations cannot co-exist as they do not logically contradict.

## Generalization from prototypical models

(THIS PART MORE EXPERIMENTAL)

If we observe 3 individuals connected in a chain a part-of b part-of
c, where we have class assertions A(a), B(a), C(c), we cannot infer
anything about As, Bs or Cs in general.

We can find the most specific class expression for each individual. E.g.

    a Type (A and part-of some (B and part-of some C))

But *not*

    A SubClassOf part-of some B

However, sometimes it may be desirable to make some kind of leap like
this, possibly introducing a modal qualifier.

If we introduce an additional assertion

    A SubClassOf prototype value a

Informally we can think of this as saying "the individual a serves as
a prototype for all As". We call this a "prototypicality assertion".

Given this, and given that we have implemented the modal axiom patterns
described above, we entail

    A SubClassOf prototypically-part-of some B

As well as

    A SubClassOf prototypically-part-of some (B and part-of some C)

And assuming transitivity of part-of:

    A SubClassOf prototypically-part-of some C

Note we also get entailment to individuals as well:

    A SubClassOf prototypically-part-of value b
    A SubClassOf prototypically-part-of value c

This is all entailed by our axioms and definitions, and not a matter
of debate. What is perhaps debatable is the utility and
appropriateness of this. When does it suffice to say something is
"prototypical" (or any other modal qualifier)? When does this yield
unintended consequences?

At the risk of circular reasoning, I would say this is appropriate
whenever one regards a certain state-of-affairs as prototypical, and
useful whenever one wishes to make queries at the class level about
prototypical relationships. For example, even though I do not wish to
state that all Shhs ar involved in heart development, I may wish to
make DL queries for "M-involved-in Heart-Development" and get back Shh
for some modal operator M.

As far as unintended consequences go, so long as we restrict our ABox
assertions to things that (circularly) we deem to hold prototypically,
all entailments are intended (tautology). This is potentially a weak
point, that seems to rely on the closed world assumption to preserve
intendedness. In the real world, our assertions are a subset of the
web of true sentences that hold, not all of which we would wish to
treat as prototypical (e.g. they may connect to a particular physical
organism that is unique in its own way, such as being wormlike or
tentacled).

Practically, I would argue that this is not a problem. Formally, we
are dividing the ABox into two - a part that we map to observed
individuals in the world, and another part that is intentionally
circumscribed / underspecified and has no commitment to a mapping to
*specific* observed individuals in the world. This second ABox can be
seen as having TBox-like characteristics, which are realized when we
make prototypicality assertions, which can be viewed in some sense as
"weaker" subclass axioms.

## Applications to material entity ontologies

(THIS PART EVEN MORE EXPERIMENTAL)

One issue with existing material entity ontologies such as anatomy
ontologies is the co-reference issue.

E.g. given a pair of reciprocal axioms:

    Limb SubClassOf part-of some Tetrapod
    Tetrapod SubClassOf has-part some Limb

First of all, the assertion of dual TBox axioms can be unintuitive to
those not versed in DLs. It feels redundant (but it's not). Second,
the ontology above admits some unintended models, e.g. given:

    Limb(limb1)
    Limb(limb2)
    Tetrapod(t1)
    Tetrapod(t2)
    t1 != t2
    limb1 != limb2

The following is a model:

    limb1 part-of t1 has-part limb2 part-of t2

This could potentially be extended to a strange cyclical daisy chain
of tetrapods, or some Borgesian infinite tetrapod loop.

Similarly, it is impossible to represent a cyclic structure in a TBox,
due to their tree properties. It is impossible to distinguish a linear
chain of carbons from a cycle of carbons due to the co-reference
problem.

On a practical level, this can lead to ontologies that are too weak
for certain kinds of query-answering. For anatomy ontologies designed
to answer gene expression queries there is no problem, but these are
axiomatically weak anyway.

A radically different way of building an ontology is a prototype-based
approach. Here we may start with an ABox:

    digit1 part-of autopod1
    digit2 part-of autopod1
    digit3 part-of autopod1
    digit4 part-of autopod1
    digit5 part-of autopod1
    autopod1 connected-to zeugopod1
    zeugopod1 connected-to stylopod1
    stylopod1 connected-to body1
    autopod1 part-of body1
    zeugopod1 part-of body1
    stylopod1 part-of body1

(we assume class assertions of the form X(X_n), and we also assume
everything is mutually different).

This can be drawn in a graph structure that any anatomist can
understand.

The strict model-theoretic interpretation is unambiguous. 

However, the model in itself has no predictive power or generalization
capabilities, because it is an ABox. We're simply describing a state
of affairs, and not talking about digits, limbs in general.

The traditional ontologist way to generalize would be to make TBox
axioms, but as discussed above, these can be weaker than expected due
to the tree-model no-variable property of DL. In addition, there is
the classic problem of exceptions. This is usually handled by
weakening in certain directions (e.g. has-parts are more likely to be
violated), yielding a weaker model, arbitrarily deciding some cutoff
(e.g. we rule amputated digits to ectopic structures to be out of
scope for our "canonical ontology"). This can cause problems when
integrating mutant phenotype and canonical anatomy (see Hoehndorf et
al).

A prototype-based approach arguably better recapitulates both
biologists cognitive models (see Lakoff) and biological reality
(evolution is not essentialist - it takes prototypes and tweaks them -
any "classes" may be artificial, shadows on the cave wall).

How might this work in practice?

We might start off with an ABox model such as the one above. We may
conceive of these as observations, or as a hypothetical model
(i.e. TBox-like ABox), or even if we are bold as the evolutionary ancestor.

We might then start adding assertions of the form:

  Limb SubClassOf prototype value limb1

We would then infer that limbs prototypically have-parts stylopods,
zeugopods, autopods, digits.

We _also_ infer that Limbs prototypically have autopods with 5
digits. This may or may not be a problem depending on how we wish to
use the operatir "prototypically". We have the option of making the
prototypes more restricted, e.g.

  (Limb and part_of some Human) SubClassOf prototype value limb1

Or of introducing different operators, e.g. "canonical",
"prototypically". 

Obviously this is a radically different way of approaching ontology
building. There may be disavantages in terms of not being able to
leverage DL tooling and reasoning to the same extent, especially for
error checking. New kinds of tooling, e.g. analogy-based reasoning may
be required. Some of these already exist,
e.g. DL-learner. Alteratively it could be argued that we would use the
DL tooling where it belongs and offers more freedom for modeling the
messiness of biology without forcing an essentialist template on
everything.

GETS A BIT WAFFLY HERE

There is no reasons why both approaches can't live side by side. Most
would agree that there are some things for which TBox modeling makes
sense - e.g. CARO type classes, GO slims, much of GO cell
component. There are also things for which an ABox makes
sense. E.g. data, certain kinds of observations. Then there are things
in the middle - e.g. statements about gene products and
complexes. Here it makes sense to be pragmatic, and to model according
to what kinds of questions are being asked. The framework introduced
here provides a way to move things between levels in a principled
way. From a prosaic perspective, one possibility is to auto-add
prototypicality assertions to a traditionally modeled ABox to be able
to make DL-queries using "caoable of" type relations. Similarly, the
use of "capable of" relations has been demonstrated to be useful in
ontology building, allowing the capturing of knowledge that is
essentially modal in nature.

One area in which prototypical modeling may be useful is chemical
entities . As previously mentioned, cyclic structures can be
captured. The use of modal qualifiers may be uneccessary here, we may
want to jump straight from the prototype to a (weaker, in the case of
cycles) class expression, by finding the Most Specific Class
Expression. For repeated or branching structures, some mixture may be
necessary.

There may be some advantage in anatomy, rather than creating
hierarchies of abstraction to cpature the various exceptions in
evolution. The original pre-VBO proposal may be close in spirit.

...

