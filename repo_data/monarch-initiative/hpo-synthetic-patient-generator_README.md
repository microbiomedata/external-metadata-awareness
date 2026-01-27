# Machine Learning Patient Synthesizer

Current methods of diagnosing patients based on phenotypic profiles
are limited by the absence of individual-level data. Current methods
leverage knowledge bases that aggregate data from multiple patients
(i.e. HPO annotations). As a result, these methods cannot leverage ML
techniques and are thus suscpetible to issues arising from
non-independence of phenotypes.

Methods such as BOQA make assumptions of independence between
phenotypes, and can penalize too heavily depending on ontology
structure. Currently the best performing method is Resnick similarity,
which relies on information content of shared phenotypes. Best match
averages are typically applied. This is problematic since it does not
provide a natural way to incorporate frequency, negation or prior
knowledge about relationships between phenotypes and other
properties. For example, if a disease hallmark phenotype has adult
onset then we don't expect to see this in an NICU patient. Similarly
for sex-specific phenotypes.

ML methods such as CNNs and decision tree methods (C4.5, RFs) are
particularly good in these situations. A DT may learn to weight
different phenotypes depending on what other phenotypes and properties
are present, e.g:

```
IF age >= 16:
    IF Dilated_cardiomyopathy > 0:
       THEN: <...this part of the tree will
                 boost for OMIM:605362, which only shows this
                 phenotype for adult onset>
    ELSE IF <...other phenotype that serves as
                a better predictor for younger patients...>
```

Similarly a NN with may learn these nonlinearities in hidden layers.

But collecting sufficient data for patients with rare diseases is a
non-trivial task. However, we can leverage the knowledge in ontologies
and aggregate association databases (knowledge bases) to generate
synthetic databases for ML training.

Here we describe a KB2DB procedure using HPO association data and HPO
to generate synthetic patients for input into scikit Decision Tree
methods.

## Algorithm

For each disease we generate a sample of N synthetic patients.

Each patient has a phenotypic sex assigned assigned with probability
`{0.5, 0.5}`, unless we have prior knowledge about the sex
distribution of the disease.

Each patient is also assigned a random age, drawn from the set of HPO
onset qualifiers. The distribution is assigned ad-hoc. If we know the
disease is lethal at a certain onset then the probability for this
onset and above is zero. We store the age as a float indicating age in
years.

If there is a known causative gene for this disease, the patient is
assigned this as a causative gene. TODO: For CNVs we sample a CNV
interval and take all genes in that range. TBD: If the gene is known
to be in a particular chrosomosal range, then we assign a gene
randomly.

For each annotation `A` to that disease, we assign a phenotype `A.phenotype`
to the patient with probability `p`, where `p` is assigned according
to the Frequency column in HPO. If no frequency is annotated, then the
probability is set according to a combination of the method and the
source (ORDO assignments may have different probabilities, as might IEAs).

If the patient's age is more than the onset age for the association,
then we set `p=0` (TBD: close to zero if the range is close).

If a phenotype is assigned to a patient, then all ancestor phenotypes
are also assigned.

We also attach a severity to each phenotype, if specified.

We treat NOT annotation as annotations to `NOT(ph)`, and these propagate downwards.

We can also assigned ECTO terms to the patient TBD

Other demographic properties of relevance can also be added.

TBD: we also assign a probability that a patient has a comorbidity
with another disease, and repeat the phenotype assignment process,
adding to their set of phenotypes. The comorbidity could draw on
resources like COHD or JHU profiles.

We now have an individual patient `I` with properties such as age,
sex, environmental exposures and phenotypes, where these properties
are assigned randomly according to a KB-based distribution.

For each patient we generate an observational profile. This includes
similar properties, but takes into account false positives and false
negatives.

Working down the HPO graph of positive annotations, we randomly remove
a branch. This simulates the probability that a particular phenotype
or phenotypic system was not inspected. Ideally we would have
principled assignments for this. For example, it's unlikely that
severe craniofacial malformations would be missed. However, formation
of plaques in the brain are harder to observe directly.

We also spike in phenotypes simulating false positives on the side of
observation. 

## Input to ML algorithms

Many packages like scikit learn take as input dataframes where
variables must be continuous rather than categorical.

Currently we focus on Decision Trees, these have the advantage of
introspectability, which is highly important for reporting results. We
can even imagine a system whereby clinicians can disagree with a
learned DT, with this being fed back and fed into future construction.

We turn each observation into a vector, with target class being
disease or gene as appropriate.

Each HPO class becomes a column, with a value [-1,1], where 1
indicates presence and high severity, and -1 indicates absence.

Age is represented directly as a float.

Phenotypic sex can be represented by a single column with values
{0,1}. Continuum representations are a possibility but this may be
represented by a different column.

Optionally, we can represent opposites. We first create pairs of DP
templates (for example, incSize and decSize). For each pair, we create
a column for each unique value (e.g. "femur size"). If a phenotype
maps to a tuple in either of the pairs, we populate the column value
with +1 or -1 respectively.

The target label will be the disease or gene depending on use case.

Depending on the algorithm, we may want to split this into T
classification tasks. For example, we may want to make a decision tree
for each disease.

## Running

```
./bin/gen-patients.py --help
Usage: gen-patients.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  generate    Generate synthetic patients
  gentrain    Build classifiers, taking normalized HPOA as...
  preprocess  Parses the HPO (new) file and writes a new...
  train       Build classifiers, taking synth observation...
```


Example decision tree for  Fanconi-Bickel Syndrome

![img](docs/OMIM_227810.png)

## Testing/Evaluation

Ideally we would have ground-truth data to test against. In practice
this can be hard to obtain sufficient data.

Of course we can take the synthetic dataset and split into training, test etc.

TODO

## Extensions

### Use of basic biology (GO) and Model Organism data

We can simulate patients with deleterous variants in different
genes. We then assign human phenotypes to the patient with `Pr(Ph|G)`,
where this is derived from GO annotations and non-human phenotype
associations.

### Environment and common disease

ECTO can be treated as any other properties. It could be treated as a
target class if the disease is known. It can also serve as knowledge
that can help with a genetic diagnosis.

### Disease subtypes and MONDO

### Temporal progression

The above method creates a synthetic observation profile for a patient
at a particular age.

We can extend this 

### Family History

We can also simulate a family history for each synthetic patient. We
leverage knowledge about disease inheritance to assign phenotypes to
family members.

For simulating observational noise we can account for the fact that
knowledge of family history may be vague (e.g. "do you have history of
cancer" or "heart disease").

## Comparisons

SMOTE is a means of generating samples from small datasets. SMOTE is a
knowledge-free technique.

