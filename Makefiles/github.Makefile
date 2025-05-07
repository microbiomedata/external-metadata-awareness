RUN=poetry run

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif

# GitHub API Token (can be set via GITHUB_TOKEN environment variable)
ifdef GITHUB_TOKEN
  TOKEN_OPTION := --token $(GITHUB_TOKEN)
endif

# Default values for GitHub repositories
GITHUB_OWNER ?= microbiomedata
GITHUB_REPO ?= nmdc-schema
MIN_TAG ?= v7.1.0
OUTPUT_PATH ?= local/github-release-notes.md

.PHONY: fetch-github-releases

fetch-github-releases:
	@date
	@echo "Fetching GitHub releases from $(GITHUB_OWNER)/$(GITHUB_REPO) from tag $(MIN_TAG)..."
	@mkdir -p local
	$(RUN) fetch-github-releases \
		--owner $(GITHUB_OWNER) \
		--repo $(GITHUB_REPO) \
		--min-tag $(MIN_TAG) \
		--output $(OUTPUT_PATH) \
		$(TOKEN_OPTION) \
		--verbose
	@date

# Usage examples:
# make -f Makefiles/github.Makefile fetch-github-releases
# make -f Makefiles/github.Makefile fetch-github-releases GITHUB_OWNER=some-org GITHUB_REPO=some-repo MIN_TAG=v1.0.0 OUTPUT_PATH=local/custom-notes.md
# GITHUB_TOKEN=your_token make -f Makefiles/github.Makefile fetch-github-releases