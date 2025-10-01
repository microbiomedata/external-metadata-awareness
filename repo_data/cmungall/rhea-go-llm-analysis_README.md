# RHEA-GO Mapping LLM Analysis

This repo is for tracking the analysis of the mappings between GO and RHEA using LLMs.

Note this repo follows a generic templated structure, in future it may be more customized for the GO use case

## Background

GO maps to RHEA for leaf node reactions. RHEA and GO also mutually map to other databases.

In principle the mappings between GO and RHEA should mean "equivalent" (or we refine mappings to be broad/narrow, etc).

## Approach

We ran the OAK `validate-mappings` command on the GO-RHEA mappings through a variety of different LLMs:

- GPT-4
- GPT-4-turbo
- GPT-3.5-turbo
- Claude-opus
- Gemini-Pro
- Mixtral (via Groq)
- Llama2 (via Groq)
- Mixtral-Large

In some cases API responses we too flaky, so any that yielded < 100 results were dropped.

See [How to use LLMs in OAK](https://incatools.github.io/ontology-access-kit/howtos/use-llms) for details on `validate-mappings`

__NOTE__ in future it may make sense to write specific prompts for RHEA and GO but for now for simplicitly we use the generic command,
which makes use of the obo-db-ingest version of RHEA.

## Results

See [notebooks](notebooks) for the results of the analysis.

The pivoted table is also here:

https://docs.google.com/spreadsheets/d/1yFD24UT_Bc76mbwAie65KQEqfEVVIeFljrUy0HpHhNI/edit#gid=293565601

Consensus scores for individual models:

0,claude-3-opus-generic,0.827068
1,gpt-4-generic,0.50365
2,gpt3t-prompted,0.429787
3,gpt4full-generic,0.578231
4,groq-llama-generic,0.691667
5,mixtral-prompted,0.319588

## EXAMPLE RESULTS

Here we show one example of a mapping for which there was broad consensus across the models that there was a problem:

### Pair: GO:0003842 - RHEA:24882

SUBJECT:

Name: 1-pyrroline-5-carboxylate dehydrogenase activity Definition: H2O + L-glutamate 5-semialdehyde + NAD+ = 2 H+ + L-glutamate + NADH. Relationships:

OBJECT:

Name: (S)-1-pyrroline-5-carboxylate + 2 H2O + NADP(+) = H(+) + L-glutamate + NADPH Definition: None Relationships:

PROBLEMS: 6 (confidence: 0.7000000000000001)
* predicate_id: skos:broadMatch
* claude-3-opus-generic_info: The subject and object are not an exact match. The subject describes the activity of the enzyme 1-pyrroline-5-carboxylate dehydrogenase, which catalyzes a reaction involving L-glutamate 5-semialdehyde, NAD+, L-glutamate, and NADH. The object, on the other hand, describes a chemical reaction involving (S)-1-pyrroline-5-carboxylate, H2O, NADP+, H+, L-glutamate, and NADPH. While the reactions are related, they differ in substrates and products.
* gpt-4-generic_info: The chemical reactions and cofactors do not match exactly, indicating these are not the same activities. Specifically, the cofactor NAD+ in the SUBJECT does not match NADP(+) in the OBJECT, and NADH does not match NADPH. Additionally, the number of H2O molecules is different.
* gpt3t-prompted_info: The reaction substrates and products do not match between the SUBJECT and OBJECT. Modification of one of the entities or a different PREDICATE may be needed.
* gpt4full-generic_info: The SUBJECT and OBJECT are not identically matched. The cofactor NAD in the SUBJECT is not the same as NADP in the OBJECT. The number of water molecules involved also differs.
* groq-llama-generic_info: The predicate 'skos:exactMatch' is incorrect as the SUBJECT and OBJECT do not describe the same entity. The SUBJECT describes an enzymatic activity that converts 1-pyrroline-5-carboxylate to L-glutamate 5-semialdehyde, while the OBJECT describes a reaction involving (S)-1-pyrroline-5-carboxylate and NADP(+).
* mixtral-prompted_info: The subject and object do not represent the same reaction, although they are related. The subject is a dehydrogenase activity that converts 1-pyrroline-5-carboxylate to glutamate using NAD+ as a cofactor, while the object is the reverse reaction that converts glutamate to 1-pyrroline-5-carboxylate using NADP+ as a cofactor. The predicate suggests that the subject and object are identical, but they are not.
* claude-3-opus-generic_suggested_modifications: ; 
* gpt-4-generic_suggested_modifications: ; 
* gpt3t-prompted_suggested_modifications: ; 
* gpt4full-generic_suggested_modifications: No modification needed; Change 'NADP(+) = H(+) + L-glutamate + NADPH' to 'NAD+ = 2 H+ + L-glutamate + NADH'. And also remove '2 H2O + ' from the OBJECT
* groq-llama-generic_suggested_modifications: None; Change '(S)-1-pyrroline-5-carboxylate' to '1-pyrroline-5-carboxylate' to accurately reflect the substrate.
* mixtral-prompted_suggested_modifications: ; Consider changing the object to: 1-pyrroline-5-carboxylate = L-glutamate + NAD(P)H + H+
* claude-3-opus-generic_suggested_predicate: skos:closeMatch
* gpt-4-generic_suggested_predicate: 
* gpt3t-prompted_suggested_predicate: 
* gpt4full-generic_suggested_predicate: No modification needed
* groq-llama-generic_suggested_predicate: Change 'skos:exactMatch' to 'skos:closeMatch' or 'skos:relatedMatch' to reflect the related but distinct nature of the SUBJECT and OBJECT.
* mixtral-prompted_suggested_predicate: Consider changing the predicate to a more appropriate one, such as skos:relatedMatch or skos:closeMatch