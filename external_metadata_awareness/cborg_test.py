import openai
import os
from dotenv import load_dotenv

# Load environment variables from local/.env
load_dotenv(os.path.join('..', 'local', '.env'))

client = openai.OpenAI(
    api_key=os.environ.get('CBORG_API_KEY'),  # Retrieve API key from environment variables
    base_url="https://api.cborg.lbl.gov"  # Local clients can also use https://api-local.cborg.lbl.gov
)

models = [
    "lbl/llama-3",  # LBNL-hosted model (free to use)
    "lbl/command-r-plus",  # LBNL-hosted model (free to use)
    "openai/gpt-3.5-turbo",
    "openai/gpt-4o",
    "anthropic/claude-haiku",
    "anthropic/claude-sonnet",
    "anthropic/claude-opus"
]

for m in models:
    try:
        response = client.chat.completions.create(
            model=m,
            messages=[
                {
                    "role": "user",
                    "content": "What is the Lawrence Berkeley National Laboratory?"
                }
            ],
            temperature=0.0  # Optional: set model temperature to control amount of variance in response
        )

        print(f"Model: {m}\nResponse: {response.choices[-1].message.content}")
    except:
        print(f"Error calling model {m}")
