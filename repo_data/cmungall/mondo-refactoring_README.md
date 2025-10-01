# Mondo refactoring

Code to discover

- candidate term obsoletions
- candidate edges to remove

Primarily based on evidence only coming from a single less trusted source

## Running

See [Makefile](Makefile)

This orchestrates:

1. serial composition of SQL views
2. OAK code to take view results and apply obsoletion
