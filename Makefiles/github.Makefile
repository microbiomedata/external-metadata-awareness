RUN=poetry run

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif

# GitHub API token. Taken from the gh CLI, which stores it in the macOS Keychain,
# so no copy is kept in a .env file. An explicit GITHUB_TOKEN still wins if set.
#
# ifdef was wrong here: in Make it is true for a variable set to empty, so an empty
# GITHUB_TOKEN produced "--token " with no value and the command got a malformed flag
# instead of falling back to unauthenticated.
# Treat unset and set-but-empty the same way, so both fall back to gh.
ifeq ($(strip $(GITHUB_TOKEN)),)
  GITHUB_TOKEN := $(shell gh auth token 2>/dev/null)
endif
ifneq ($(strip $(GITHUB_TOKEN)),)
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