#!/bin/bash

# ==============================================================================
# GitHub Pull Request Participant Extraction
# ==============================================================================
#
# PURPOSE:
#   Extracts and counts unique GitHub contributors from pull request JSON data
#   for the microbiomedata/nmdc-metadata repository.
#
# USAGE:
#   ./sample_extraction_commands.sh
#
# PREREQUISITES:
#   - github_issues_prs/microbiomedata_nmdc-metadata_pulls.json: GitHub API JSON data
#
# INPUT FORMAT:
#   JSON file containing GitHub pull request data with "login" fields for users
#
# OUTPUT:
#   github_issues_prs/microbiomedata_nmdc-metadata_pulls_participants.txt
#   Format: "<count> <username>" sorted by frequency
#
# PIPELINE EXPLANATION:
#   1. sed 's/^ *"/"/' - Remove leading whitespace before quotes
#   2. grep '"login":' - Extract lines containing user login information
#   3. sort - Sort alphabetically for consistent grouping
#   4. uniq -c - Count occurrences of each unique login
#
# ==============================================================================

sed 's/^ *"/"/' github_issues_prs/microbiomedata_nmdc-metadata_pulls.json | grep '"login":' | sort | uniq -c > github_issues_prs/microbiomedata_nmdc-metadata_pulls_participants.txt