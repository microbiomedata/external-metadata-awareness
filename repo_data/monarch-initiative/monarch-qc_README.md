# Monarch Ingest Dashboard
The purpose of this project is to create a dashboard for viewing statistics and QC for the Monarch Knowledge Graph and Ingest pipeline. The main functionality is created in Node.js using Vue + Vite web-authoring platforms using Typescript for data processing and yarn for node module management.

This dashboard uses Node js and Vue, with the Vite build system. For deatailed instructions on the development and build environment please see CONTRIBUTING.md
Long-term this repository may also host the scripts and infrastructute to run the QC on existing Monarch KGs retroactively including producing new QC reports on builds of older KGs. Currently, this is out of scope of the current dashboard and we are only working on implementing a simplest functioning product.
# Key Project decisions
We have made these key decisions for the implementation of the Monarch Ingest Dashboard

Notes from tutorial/planning meeting with Vincent:
These are the decisions we've made for the new Monarch Ingest Dashboard 
1. Use Vite for build system right now. It is newer and vue-cli is maintenance only (Depracated)
2. Use Vue 3 since we're just starting to avoid a migration in the future.
3. Use Composition API for Vue 3 - It is pythonic and just generally cleaner and visualy easier to understand
4. Use Typescript, there really isn't any reason not to - the newer tools all support it well now
5. Use yarn instead of npm (although yarn still requires npm...) it may be faster and possibly more secure, Vincent has also expressed experiencing fewer problems.
6. Use newest nodee.js (LTS) - Currently 18.12.1
7. Vincent recommends VS Code for IDE, might be advantageous to use the sae IDE.
8. We may want to set up ES-lint for linting... not currently default with Vite


Some other thoughts:
1. Make UI components as dumb as possible (reasonable) and keep transformation and state in TypeScript separate from components.
2. Fetch teh QC Report at top level and set as a global variable for further processing downstream

Vincent spent a little time with us and mocked up a (functioning) QC Report loader. We'll need to convert to Yaml and process the data into something useable but it is a great start.


## Project setup
For project setup, please refer to the CONTRIBUTING.md for complete setup and development environment instructions. The CONTRIBUTING.md document also includes initial setup of the environment and ongoing changes for getting started on development.


---

This section is from the initial setup of Vue + Vite and is currently only kept for refernce purposes

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

## Recommended IDE Setup

- [VS Code](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar)

## Type Support For `.vue` Imports in TS

Since TypeScript cannot handle type information for `.vue` imports, they are shimmed to be a generic Vue component type by default. In most cases this is fine if you don't really care about component prop types outside of templates. However, if you wish to get actual prop types in `.vue` imports (for example to get props validation when using manual `h(...)` calls), you can enable Volar's Take Over mode by following these steps:

1. Run `Extensions: Show Built-in Extensions` from VS Code's command palette, look for `TypeScript and JavaScript Language Features`, then right click and select `Disable (Workspace)`. By default, Take Over mode will enable itself if the default TypeScript extension is disabled.
2. Reload the VS Code window by running `Developer: Reload Window` from the command palette.

You can learn more about Take Over mode [here](https://github.com/johnsoncodehk/volar/discussions/471).
