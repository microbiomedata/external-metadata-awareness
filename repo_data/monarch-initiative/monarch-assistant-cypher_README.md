# Monarch Assistant (2.0 beta, Neo4j)

This repo contains initial work on a Monarch Assistant 2.0, a followup to the [Monarch Assistant](https://github.com/monarch-initiative/monarch-assistant) with ability to query the Neo4j-hosted KG directly via cypher queries. 

### Quickstart

While a public version of the Neo4j KG is not yet available, you can run one yourself with docker via https://github.com/monarch-initiative/monarch-neo4j.

Create `.env` ala:

```
OPENAI_API_KEY=<your key>
NEO4J_BOLT=bolt://<neo4j ip>:7687
```

And run `make install app`.

### Contents summary

There are several pieces here which should someday end up in individual repos:

- `kani_streamlit.py` - An extension of the [Kani](https://kani.readthedocs.io/en/latest/) LLM framework for simple Streamlit applications with some fun features. See `agents.py` and `app.py` for usage.

- GPT-4 is not great at at writing cypher queries off the bat, frequently forgetting vars in `WITH` clauses, backtics when labels contain special characters, and generally unaware of a specific graph's schema. Providing KG-specific examples (e.g. in the system prompt) helps considerably, but developing these is tricky, unless you know both cypher and the KG contents well. In addition to defining a monarch assistant agent, `agents.py` also defines a "graph explorer" agent that can interactively develop competency questions, send them to a query agent for testing, and an evaluation agent for assessment and refinement. Passing competency questions can be saved to local storage and downloaded by the user, though lately I've just been copy-pasting them from the chat into the collection in `monarch_competency_questions_1.json`.