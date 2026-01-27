This repo serves two purposes

 * as a test of the kboom ontology merging process
 * to provide a solution for the radiation branch of ENVO, see https://github.com/EnvironmentOntology/envo/issues/255

## Inputs

Select ontology subsets:

 * [rad-eo.obo](rad-eo.obo)
 * [rad-go.obo](rad-go.obo)
 * [rad-ncit.obo](rad-ncit.obo)
 * [rad-pato.obo](rad-pato.obo)
 * [rad-snomed.obo](rad-snomed.obo)
 * [rad-xco.obo](rad-xco.obo)
 * [rad-zeco.obo](rad-zeco.obo)

We treat pseudo-equivalents as equivalents for the purposes of obtaining a common view. For example, response-to-X == exposure-to X == X

## Examples

For this particular problem set the resolution is relatively straightforward as most mappings are unambiguously equivalent

This example highlights an incomplete non-trivial merge:

![img](examples/EM-radiation.png)

Note that GO lexically treats radiation == EM radiation (EXACT syn),
which creates the possibility for inconsistent
configurations. Consistently resolved here.

Note there is no inference that light is EM, the information is not present sufficiently

