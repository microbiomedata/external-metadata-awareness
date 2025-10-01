## Langchain/langflow test

[Langflow]() is a GUI for experiments with langchain; `langflow_monarch_wrapper.json` can be imported to it (and langchain) and implements an OpenAPI agent toolkit, ostensibly mimicking ChatGPT plugins. The corresponding `openapi.json` is the JSON spec and assumes the [oai-monarch-plugin](https://github.com/monarch-initiative/oai-monarch-plugin) is running on localhost port 3434.

**Try it**: 

* Run [oai-monarch-plugin](https://github.com/monarch-initiative/oai-monarch-plugin) on localhost:3434 via `make dev`
* run langflow
* import `langflow_monarch_wrapper.json` in the langflow UI
* open/load `openapi.json` in the JSON block in the UI
* enter OpenAI api key in the LLM block
* use the "chat" icon in the lower right (and watch the langflow logs)

Altnernatively it can be run via python (not tested, so I'm not sure where the JSON spec and API key are provided):

```
from langflow import load_flow_from_json

flow = load_flow_from_json("langflow_monarch_wrapper.json")
# Now you can use it like any chain
flow("What genes are involved in Marfan's syndrome?")
```

## Basic tool using agent

The `chat_thought_agent.ipynb` notebook contains experiments allowing gpt-3.5/4 to call tools as a set of pre-determined safe python functions. It's in early stages, the model
isn't always following directions well (still to try moving some of the instructions out of the system command, and using test functions other than `sum` and `product` which may be confusing for it)

Add your `OPENAI_API_KEY` to `.env`, and see `Makefile` for running.