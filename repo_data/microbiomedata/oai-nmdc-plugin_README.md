# oai-nmdc-plugin

ChatGPT plugin and wrapper for NMDC  API.

## How to run

### Get access to the ChatGPT plugin developer program

Unfortunately you will need to be accepted to the OpenAI developer program

Join the waitlist [here](https://openai.com/waitlist/plugins)

It may be possible to grant permissions broadly across an organization? https://community.openai.com/t/developer-access-for-colleagues/157315

### Run the server

```bash
poetry install
sh dev_run.sh
```

This will start up a server on 3535

Check it works:

- http://localhost:3535/.well-known/ai-plugin.json
- http://localhost:3535/docs

### Register

Go to https://chat.openai.com/

If you have plugin access, you'll see an option

Select the plugin model from the top drop down, then select “Plugins”, “Plugin Store”, and finally “Install an unverified plugin” or “Develop your own plugin”.

Enter `localhost:3535`

You should see the plugin activated

If you run into difficulties, see https://platform.openai.com/docs/plugins/introduction

## Acknowledgements

Based on a template created by [Shawn O'Neill](https://github.com/oneilsh) of TISLab/Monarch Initiative.
See: [Monarch ChatGPT plugin](https://github.com/monarch-initiative/oai-monarch-plugin)
