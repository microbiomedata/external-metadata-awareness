# badexperiment
Convert Index of Terms to LinkML YAML. 

TODOs: 
- convert to actual LinkML artifcats after that
- convert to DataHarmonizer template

Many moving parts = bad experiment.

Development or use within the repo requires [Poetry](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions)

## Usage within this environment
`poetry run becli`

## Publishing
Don't forget to update `version` in `[tool.poetry]`

**Note the use of initial whitespace for [keeping the PyPI password out of the zsh history](https://superuser.com/questions/352788/how-to-prevent-a-command-in-the-zshell-from-being-saved-into-history).** There are similar tricks for other shells like Bash.

```shell
setopt HIST_IGNORE_SPACE
export pypi_user='mamillerpa'
 export pypi_pw='<SECRET>'
poetry build
poetry publish --username $pypi_user --password $pypi_pw
```

## Installation outside of this repo
Aggressive cleanup?

```shell
# assume we're inside a venv virtual environment
deactivate
rm -rf venv
# purge under what circumstances?
python3.9 -m pip cache purge
python3.9 -m venv venv
source venv/bin/activate
python3.9 -m pip install --upgrade pip
pip install wheel
# check status of package under development
# don't continue with installation when
pip index versions badexperiment
# installation of pandas is slow
#   platform dependent? M1 MBA
pip install badexperiment
```

## Usage outside of this repo

```shell
becli --help
```

## Concerns

### How to create, modify and save a LinkML schema?
- Preferably with schemaview
- Otherwise direct linkml methods
- Otherwise dict -> yaml file
	
### Poetry autocomplete

### Values trying to be set on a copy of a slice from a DataFrame

> /Users/mark/sandbox/venv/lib/python3.9/site-packages/pandas/core/indexing.py:1667: SettingWithCopyWarning: 
A value is trying to be set on a copy of a slice from a DataFrame.
Try using .loc[row_indexer,col_indexer] = value instead

> See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
  self.obj[key] = value

> /Users/mark/sandbox/venv/lib/python3.9/site-packages/badexperiment/sheet2yaml.py:119: SettingWithCopyWarning: 
A value is trying to be set on a copy of a slice from a DataFrame.
Try using .loc[row_indexer,col_indexer] = value instead

> See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
  slot_to_pack[coalesced] = slot_to_pack[repaired_col_name]

> /Users/mark/sandbox/venv/lib/python3.9/site-packages/pandas/core/indexing.py:1732: SettingWithCopyWarning: 
A value is trying to be set on a copy of a slice from a DataFrame

> See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
  self._setitem_single_block(indexer, value, name)
  
