## LLM models available after installing the llm-gemini and llm-claude-3 [llm](https://llm.datasette.io/en/stable/index.html) plugins.

Most promising models **highlighted in bold**.

* OpenAI Chat: gpt-3.5-turbo (aliases: 3.5, chatgpt)
* OpenAI Chat: gpt-3.5-turbo-16k (aliases: chatgpt-16k, 3.5-16k)
* **OpenAI Chat: gpt-4 (aliases: 4, gpt4)**
* OpenAI Chat: gpt-4-32k (aliases: 4-32k)
* OpenAI Chat: gpt-4-1106-preview
* OpenAI Chat: gpt-4-0125-preview
* OpenAI Chat: gpt-4-turbo-2024-04-09
* OpenAI Chat: gpt-4-turbo (aliases: gpt-4-turbo-preview, 4-turbo, 4t)
* **OpenAI Chat: gpt-4o (aliases: 4o)**
* OpenAI Chat: gpt-4o-mini (aliases: 4o-mini)
* OpenAI Completion: gpt-3.5-turbo-instruct (aliases: 3.5-instruct, chatgpt-instruct)
* GeminiPro: gemini-pro
* **GeminiPro: gemini-1.5-pro-latest**
* GeminiPro: gemini-1.5-flash-latest
* **Anthropic Messages: claude-3-opus-20240229 (aliases: claude-3-opus)**
* Anthropic Messages: claude-3-sonnet-20240229 (aliases: claude-3-sonnet)
* Anthropic Messages: claude-3-haiku-20240307 (aliases: claude-3-haiku)
* **Anthropic Messages: claude-3-5-sonnet-20240620 (aliases: claude-3.5-sonnet)**

It can be helpful to set the `temperature` to something close to 0 for "least creative" answers, but not all models take
that parameter

`-o temperature 0.01`