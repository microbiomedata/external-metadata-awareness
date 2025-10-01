# DRAGON-AI Project Cookiecutter

A [Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/) template for projects using [CurateGPT](https://github.com/monarch-initiative/curate-gpt).

## Prerequisites

The following are required and recommended tools for using this cookiecutter and the LinkML project that it generates. This is all one-time setup, so if you have already done it skip to the [next section](#creating-a-new-project)!

  * **Python >= 3.8**
  
    LinkML tools are mainly written in Python, so you will need a recent Python interpreter to run this generator and to use the generated project.


  * **pipx**
  
    pipx is a tool for managing isolated Python-based applications. It is the recommended way to install Poetry and cruft. To install pipx follow the instructions here: https://pypa.github.io/pipx/installation/


  * **Poetry**
  
    Poetry is a Python project management tool. You will use it in your generated project to manage dependencies and build distribution files. If you have pipx installed you can install Poetry by running: 
     ```shell
     pipx install poetry
     ```
     For other installation methods see: https://python-poetry.org/docs/#installation
  
  * **Poetry behind firewalls**

    In sandboxed environments (proxy or internal repositories), you must configure poetry source in `~/.config/pypoetry/pyproject.toml` to allow software installation, illustrated below:
    ```shell
    [[tool.poetry.source]]
    name = "myproxy"
    url = "https://repo.example.com/repository/pypi-all/simple"
    priority = "default"
    ```

  * **Poetry Dynamic Versioning Plugin**: 

    This plugin automatically updates certain version strings in your generated project when you publish it. Your generated project will automatically be set up to use it. Install it by running:
    ```shell
    poetry self add "poetry-dynamic-versioning[plugin]"
    ```


  * **cruft**

    cruft is a tool for generating projects based on a cookiecutter (like this one!) as well as keeping those projects updated if the original cookiecutter changes. Install it with pipx by running:
    ```shell
    pipx install cruft
    ```
    You may also choose to not have a persistent installation of cruft, in which case you would replace any calls to the `cruft` command below with `pipx run cruft`. 

  * **OpenAI API key**

## Creating a new project

### Step 1: Generate the project files

To generate a new LinkML project run the following:
```bash
cruft create https://github.com/linkml/linkml-project-cookiecutter
```
Alternatively, to add linkml project files to pre-existing directory,
(perhaps an existing non-linkml project), pass `-f` option:
```bash
cruft create -f https://github.com/linkml/linkml-project-cookiecutter
```

### Step 2: Initialize

```bash
cd my-project-name
make bootstrap
```

TODO: document human-in-the-loop-cycle

### Step 3: Make full project

```bash
make install
make all
```
