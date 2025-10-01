# Requirements

## Capture guiding principles/decisions in this new repo (in Readme)

## Ultimate goal: Replace OWLSim to drastically reduce our bill. 

## First iteration will be semantic similarity only.  Cosine will be researched further and implemented later.

## Initialization and deployment

- inputs will be Phenio and the relevant subset of the Monarch KG (list ontologies, associations included)

- FastAPI Implementation for Semantic Search that will return a ranked set tuples (matchin score, entity)

- should still be synchronous with queries

## Performance and Efficiency (List requirements for memory and latency 

- should still be synchronous with queries

- precomputed tables using OAK

## Jaccard Similarity
 
 - Question for Nico - do we / how do we integrate uPheno or uPheno2? 
 
## Cosine Similarity

- Explore Ensmallen for this. We likely want to hold in memory all ontologies and associations (HPO + MP + uPheno) 
