# GWAS Fix Existing Obsolete Traits

A Spring-based utility application for managing obsolete EFO (Experimental Factor Ontology) traits in the GWAS database.

## Purpose

This application addresses the scenario where obsolete EFO traits and their replacement traits co-exist in the database, both potentially having linked studies and associations. The tool ensures data integrity by consolidating references to use only the current, non-obsolete traits.

## Database Modes

The application supports our two synced databases:

### Oracle Mode
Works with the relational Oracle database schema used in GWAS. Updates join tables that link studies and associations to EFO traits:
- `STUDY_EFO_TRAIT`
- `STUDY_BACKGROUND_EFO_TRAIT`
- `ASSOCIATION_EFO_TRAIT`
- `ASSOCIATION_BKG_EFO_TRAIT`

### MongoDB Mode
Works with the MongoDB document database used in GWAS Deposition. Updates trait references within study and association documents stored in MongoDB collections.

Both modes follow the same logic: identify obsolete traits via the OLS4 API, find their replacements, update all references, and clean up obsolete entries.

## What It Does

The application automatically:

1. **Discovers obsolete traits** - Queries the EBI OLS4 (Ontology Lookup Service) API to retrieve all obsolete EFO terms and their designated replacements
2. **Migrates references** - Updates all database references from obsolete traits to their replacement traits
3. **Cleans up** - Removes obsolete trait entries after successful migration

## How It Works

- Fetches paginated results from OLS4 API for all obsolete EFO terms
- Cross-references obsolete traits with the local GWAS database
- Resolves replacement trait identifiers (handles both URIs and short forms)
- Performs transactional updates to maintain data consistency
- Only processes traits where both obsolete and replacement versions exist in the database

### Run Oracle Mode
java -jar target/fix-obsolete-efos-0.0.1-SNAPSHOT.jar oracle

### Run Mongo Mode
java -jar target/fix-obsolete-efos-0.0.1-SNAPSHOT.jar mongo

Or simply add "mongo" or "oracle" to the IntelliJ (or your favourite IDE) program arguments for the run configuration.
