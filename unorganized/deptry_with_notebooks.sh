#!/bin/bash

set -euo pipefail

# Temporary output directory for converted notebooks
TMP_DIR=".nb_py"
mkdir -p "$TMP_DIR"

# Recursively find all notebooks
find . -name '*.ipynb' ! -path "./$TMP_DIR/*" | while read -r notebook; do
    # Convert to flat path using underscores to avoid collisions
    # e.g. notebooks/data/stats.ipynb -> .nb_py/notebooks_data_stats.py
    out_file=$(echo "$notebook" | sed 's|[./]|_|g').py
    jupyter nbconvert --to python "$notebook" --output "$out_file" --output-dir "$TMP_DIR"
done

# Run deptry on main source paths and converted notebooks
deptry external_metadata_awareness/ "$TMP_DIR"

# Clean up
rm -r "$TMP_DIR"

