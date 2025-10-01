# Monarch Agent Tutorial

We will be walking through the process of creating an ontology agent. The goal is to empower you as a Python developer to turbo-charge your applications with AI.

If you are curious about AI but feel intimidated by the confusing range of tools and acronyms out there, **this tutorial is meant for you**!

The intended audience is the OBO and Monarch communities, but all are welcome!

## Recording

This tutorial was a part of [the Monarch OBO Academy training](https://oboacademy.github.io/obook/courses/monarch-obo-training/).

See the [recording on YouTube](https://www.youtube.com/watch?v=Ml0YVjKnZnE)

## Pre-requisites

1. Some knowledge of Python
2. `uv` installed locally
3. An IDE or text editor (I will use cursor in the walk-through, but any should work)
4. An OpenAI API key, with `OPENAI_API_KEY` set
    * All developers in Monarch should already have a key
    * LBNL developers can use cborg, see instructions below
    * It should be possible to modify examples to use a different model, but we won't covert this in the interests of time
    * Otherwise sign up to get an OpenAI key

Additionally, some knowledge of ontologies like UBERON and the capabilities of the [OAK](https://incatools.github.io/ontology-access-kit/)
will help.

## Initializing the project

### Install uv

Follow the instructions here: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

On a mac:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Create the repo

```bash
uv init --package agent-tutorial
```

### Add dependencies

```
cd agent-tutorial
```

(or open the terminal in your IDE)

```
uv add pydantic-ai
```

## PART 1: Create a basic agent

We will be using [pydantic-ai](https://ai.pydantic.dev/).

![img](https://ai.pydantic.dev/img/pydantic-ai-light.svg#only-light)

There are many other agent frameworks available: langgraph, crew-ai, smolagents. Each has its own strengths and weaknesses and it is often
a matter of preference. 

### Create `hello_world.py`

Create this in [src/agent_tutorial/hello_world.py](src/agent_tutorial/hello_world.py)

Copy the example from here:

https://ai.pydantic.dev/#hello-world-example

Adapt it to use `openai:gpt-4o` (unless you have a )

```python
from pydantic_ai import Agent

agent = Agent(  
    'openai:gpt-4o',
    system_prompt='Be concise, reply with one sentence.',  
)

result = agent.run_sync('Where does "hello world" come from?')  
print(result.data)
"""
The first known use of "hello, world" was in a 1974 textbook about the C programming language.
"""
```

### Run it

```
uv run src/agent_tutorial/hello_world.py 
```

__TROUBLESHOOTING__ 

* do you have `OPENAI_API_KEY` set?

## PART 2: Create an agent with tools

### Add OAK as a dependency

Next we will add [OAK](https://incatools.github.io/ontology-access-kit/)

```
uv add oaklib
```

__TROUBLESHOOTING__

You may need to do this first:

```
uv add fastobo --binary fastobo==0.12.3
```

Then create a file [src/agent_tutorial/oak_agent.py](src/agent_tutorial/oak_agent.py)

We will make an agent, as before

```python
oak_agent = Agent(  
    'openai:gpt-4o',
    system_prompt="""
    You are an expert ontology curator. Use the ontologies at your disposal to
    answer the users questions.
    """,  
)```

But this time we will give an agent a *tool*

```python
@oak_agent.tool_plain
async def search_uberon(term: str) -> List[Tuple[str, str]]:
    """
    Search the UBERON ontology for a term.

    Note that search should take into account synonyms, but synonyms may be incomplete,
    so if you cannot find a concept of interest, try searching using related or synonymous
    terms.

    If you are searching for a composite term, try searching on the sub-terms to get a sense
    of the terminology used in the ontology.

    Args:
        term: The term to search for.

    Returns:
        A list of tuples, each containing an UBERON ID and a label.
    """
    adapter = get_adapter("ols:uberon")
    results = adapter.basic_search(term)
    labels = list(adapter.labels(results))
    print(f"## Query: {term} -> {labels}")
    return labels
```

Here we are using the OAK OLS adapter, configured to query [Uberon on OLS](https://www.ebi.ac.uk/ols4/ontologies/uberon)

We can test this with

```python
query = "What is the UBERON ID for the CNS?"
result = oak_agent.run_sync(query)
```

And run it:

```
uv run src/agent_tutorial/oak_agent.py 
```

Try this with some other terms. How well does it work?

## PART 3: Create an annotator agent

Then create a file [src/agent_tutorial/annotator_agent.py](src/agent_tutorial/annotator_agent.py)

We will create a bespoke data model for this agent:

```python
class TextAnnotation(BaseModel):
    """
    A text annotation is a span of text and the UBERON ID and label for the anatomical structure it mentions.
    Use `text` for the source text, and `uberon_id` and `uberon_label` for the UBERON ID and label of the anatomical structure in the ontology.
    """
    text: str
    uberon_id: Optional[str] = None
    uberon_label: Optional[str] = None

class TextAnnotationResult(BaseModel):
    annotations: List[TextAnnotation]
```

Now we'll create an agent:

```python
annotator_agent = Agent(  
    'claude-3-7-sonnet-latest',
    system_prompt="""
    Extract all uberon terms from the text. Return the as a list of annotations.
    Be sure to include all spans mentioning anatomical structures; if you cannot
    find a UBERON ID, then you should still return a TextAnnotation, just leave
    the uberon_id field empty.

    However, before giving up you should be sure to try different combinations of
    synonyms with the `search_uberon` tool.
    """,
    tools=[search_uberon],
    result_type=TextAnnotationResult,  
)
```

Note this reuses the tool from the previous example

And run it:

```
uv run src/agent_tutorial/annotator_agent.py 
```

## Using a Proxy (e.g. CBORG)

```python
cborg_api_key = os.environ.get("CBORG_API_KEY")

model = OpenAIModel(
    "anthropic/claude-sonnet",
    provider=OpenAIProvider(
        base_url="https://api.cborg.lbl.gov",
        api_key=cborg_api_key),
)
```

then, in place of code like:

```python
agent = Agent(  
    'openai:gpt-4o',
    system_prompt='Be concise, reply with one sentence.',  
)
```

Do this:

```python
agent = Agent(  
    model,
    system_prompt='Be concise, reply with one sentence.',  
)
```

## Next Steps: Aurelian

After this, we invite you to check out [aurelian](https://github.com/monarch-initiative/aurelian) and to try some of the ready-made agents and tools, and to contribute to this library!
