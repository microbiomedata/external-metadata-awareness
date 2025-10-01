# Contextualizer Project: Comprehensive Guide

## Project Overview

The Contextualizer project is an AI agent framework built on `pydantic-ai` that uses the Berkeley Lab's CBORG API to
access various language models. This guide combines official documentation, notes, and practical experience to help you
get started with the project.

## Prerequisites

- Python 3.10+ installed (3.10+ is specified in pyproject.toml)
- `uv` installed (a faster alternative to pip)
- CBORG API key (required for all agents)
- Google Maps API key (only required for map functionality in geo_agent.py)
- python-dotenv package (installed automatically as a dependency)

## 1. Understanding The CBORG API

### What is CBORG?

CBORG is Berkeley Lab's AI Portal that provides secure access to various AI models. The CBORG API server is an
OpenAI-compatible proxy server built on LiteLLM, which means it can be used as a drop-in replacement for OpenAI's API.

### Available Models

The CBORG API provides access to various models. Based on testing, your account may have access to:

- **LBL-hosted models**:
    - lbl/cborg-chat:latest
    - lbl/cborg-vision:latest
    - lbl/nomic-embed-text

- **Commercial models**:
    - openai/gpt-4.1-nano
    - aws/claude-haiku
    - (potentially others)

Note that not all models listed in documentation may be available to your specific API key. You can use the test
connection script below to see which models are accessible to you.

## 2. Environment Setup

### Install UV

```bash
# Install UV on Unix/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH if needed
```

### Create Virtual Environment

```bash
# Navigate to your repository
cd contextualizer

# Create a virtual environment with UV
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install development dependencies
uv pip install -e .
```

### Python Version Issues

The project requires Python 3.10+. If you're using pyenv and encounter version issues:

```bash
# Install Python 3.10 with pyenv
pyenv install 3.10

# Or remove .python-version file to use UV's Python directly
rm .python-version
```

## 3. API Key Configuration

### Set Up Your CBORG API Key

You have several options:

1. **Create a .env file** (recommended):
   ```bash
   echo "CBORG_API_KEY=your_cborg_api_key_here
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here" > .env
   ```
   
   The project uses python-dotenv to load environment variables from this file.

2. **Export in your shell**:
   ```bash
   export CBORG_API_KEY="your_cborg_api_key_here"
   export GOOGLE_MAPS_API_KEY="your_google_maps_api_key_here"  # Only if using map functions
   ```

3. **Use the .venv/bin/python approach**:
   ```bash
   CBORG_API_KEY="your_cborg_api_key_here" .venv/bin/python your_script.py
   ```

### How to Get the CBORG API Key

- If affiliated with Berkeley Lab: CBORG is free for employees with @lbl.gov, @es.net, or @nersc.gov email.

## 4. Running Agents

You can run any of the agents using the Makefile:

```bash
# Run the hello world example
make hello-world

# Run the geo agent
make geo

# Run the soil agent
make soil

# Run the weather agent
make weather

# Run the Wikipedia animal QA agent
make wiki
```

## 5. Understanding and Using Agents

### Common Agent Structure

Most agents in this repository follow this pattern:

1. Load environment variables and API key (using python-dotenv)
2. Configure an AI model with the CBORG provider
3. Create an Agent with a system prompt
4. Register tools using decorators
5. Execute queries with the agent

### Agent Tools

Tools can be defined and registered using the `@agent.tool_plain` decorator, as shown in geo_agent.py:

```python
@geo_agent.tool_plain
def get_elev(
        lat: float, lon: float,
) -> float:
    """
    Get the elevation of a location.

    :param lat: latitude
    :param lon: longitude
    :return: elevation in m
    """
    print(f"Looking up elevation for lat={lat}, lon={lon}")
    return elevation((lat, lon))
```

### Available Agents

- **hello_world.py**: Simple "Hello World" example agent
- **geo_agent.py**: Geographic data agent (needs GOOGLE_MAPS_API_KEY for map functionality)
- **soil_agent.py**: Soil science agent
- **weather.at.py**: Weather information agent
- **wikipedia_animal_qa.py**: Wikipedia animal information agent
- **evelation_info.py**: Tool for elevation information (used by geo_agent)

## 7. Troubleshooting

### Module Not Found Errors

If you see errors like: `ModuleNotFoundError: No module named 'agent_test'`:

1. Use the virtual environment Python directly (as configured in the Makefile):
   ```bash
   .venv/bin/python -m pytest tests/
   # or use the Makefile targets
   make test-agent
   make test-minimal
   ```

2. Or make sure you've activated the virtual environment:
   ```bash
   source .venv/bin/activate
   pytest tests/
   ```

### API Key Authentication Errors

If your CBORG API key isn't being loaded:

1. Check that your `.env` file exists and contains the correct key
2. Verify that python-dotenv is installed (it should be installed automatically with dependencies)
3. Ensure the .env file is in the root directory of the project

### Model Availability Errors

If you see errors related to model availability:

1. Update your agent code to use an available model (like "lbl/cborg-chat:latest")
2. Check the error message for specific details about the failure

## 8. Running Tests

The repository includes tests in the `tests/` directory with corresponding targets in the `Makefile`:

```bash
# Run all tests
make test-agent test-minimal

# Run specific tests
make test-agent
make test-minimal
```

The Makefile uses `.venv/bin/pytest` to ensure the correct Python environment is used.

For more reliable testing, you can also run tests directly:

```bash
.venv/bin/pytest tests/test_agent.py -v
.venv/bin/pytest tests/test_minimal_agent.py -v
```

## 9. Code Style Guidelines

The project follows these coding standards:

- **Imports**: Standard grouping (stdlib, third-party, local)
- **Type Annotations**: All functions should use Python type hints
- **Docstrings**: Multi-line docstring with params/returns (triple quotes)
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Error Handling**: Use try/except with logging, avoid silent failures
- **Tools**: Use @agent.tool_plain decorator for agent functions
- **Async**: Both sync and async functions are used; choose appropriately

## 10. If You Don't Have Berkeley Lab Access

If you're not affiliated with Berkeley Lab and can't get a CBORG API key, you can modify the repository to use other LLM
providers:

1. Change the base_url to your preferred provider
2. Update the model names to ones available on that provider
3. Adjust the API authentication methods as needed

Example for using OpenAI directly:

```python
ai_model = OpenAIModel(
    "gpt-4-turbo",  # Use your available model
    provider=OpenAIProvider(
        api_key=os.getenv("OPENAI_API_KEY")),  # No need for base_url with direct OpenAI
)
```

## References and Resources

- CBORG API Portal: https://cborg.lbl.gov/
- API Documentation: https://cborg.lbl.gov/api_docs/
- API Examples: https://cborg.lbl.gov/api_examples/
- Pydantic-AI: Framework for building AI agents used by this project
