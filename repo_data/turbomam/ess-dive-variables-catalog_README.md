# ess-dive-variables-catalog
Tools for building a catalog of variables in ESS-DIVE reporting formats

Source data
- https://github.com/ess-dive-workspace repos
  1. [essdive-soil-respiration](https://github.com/ess-dive-workspace/essdive-soil-respiration)
  2. [essdive-workspace-guide](https://github.com/ess-dive-workspace/essdive-workspace-guide)
  3. [reporting-format-template-repo](https://github.com/ess-dive-workspace/reporting-format-template-repo)
  4. [essdive-dataset-metadata](https://github.com/ess-dive-workspace/essdive-dataset-metadata)
  5. [essdive-model-data-archiving-guidelines](https://github.com/ess-dive-workspace/essdive-model-data-archiving-guidelines)
  6. [essdive-sample-id-metadata](https://github.com/ess-dive-workspace/essdive-sample-id-metadata)
  7. [essdive-amplicon](https://github.com/ess-dive-workspace/essdive-amplicon)
  8. [essdive-hydrologic-monitoring](https://github.com/ess-dive-workspace/essdive-hydrologic-monitoring)
  9. [essdive-location-metadata](https://github.com/ess-dive-workspace/essdive-location-metadata)
  10. [essdive-csv-structure](https://github.com/ess-dive-workspace/essdive-csv-structure)
  11. [essdive-uas](https://github.com/ess-dive-workspace/essdive-uas)
  12. [essdive-file-level-metadata](https://github.com/ess-dive-workspace/essdive-file-level-metadata)
  13. [essdive-water-soil-sed-chem](https://github.com/ess-dive-workspace/essdive-water-soil-sed-chem)
  14. [essdive-github-systematic-review](https://github.com/ess-dive-workspace/essdive-github-systematic-review)
  15. [essdive-leaf-gas-exchange](https://github.com/ess-dive-workspace/essdive-leaf-gas-exchange)

### 🛠️ Technologies Used in `ess-dive-variables-catalog`

#### 🐍 Programming Language & Tooling
- **Python ≥3.10**
- **Click** – for building CLI commands
- **Requests** – for interacting with the GitHub API

#### 📦 Project Layout & Build System
- `src/` layout – with main package in `src/essdive_catalog/`
- **PEP 621**-style `pyproject.toml`
- Editable install via `uv pip install -e .`
- Script entry point defined in `[project.scripts]` as `essdive-catalog`

#### 🧪 Environment Management
- **`uv`** – for virtual environment creation and dependency installation
- Local `.venv/` used and activated via `uv venv`

#### 🛠️ Automation & Build
- **Makefile**-based automation
  - Real file targets (e.g., `data/raw/essdive_repo_urls.txt`)
  - `$(RUN)` abstracts `uv run`
  - No `.PHONY` targets unless necessary

#### 🗃 Version Control & Licensing
- Hosted on GitHub at [turbomam/ess-dive-variables-catalog](https://github.com/turbomam/ess-dive-variables-catalog)
- Licensed under **BSD 3-Clause**
- Uses `.gitkeep` to track empty folders in `data/raw/`

#### 🧠 Tested IDE
- PyCharm
- `src/` marked as **Sources Root**
- `.venv/bin/python` used as interpreter


