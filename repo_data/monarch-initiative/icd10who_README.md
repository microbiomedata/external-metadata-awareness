# Mondo ICD10WHO Ingest
## Setup
1. Setup API keys
   1.1. Go to https://icd.who.int/icdapi and look for information about getting API Keys.
   1.2. Follow any steps there to get API keys.
   1.3. Based on `/env/.env.example`, create a file called `/env/.env`, and fill in `CLIENT_ID`
   and `CLIENT_SECRET` with what you get from previous step.

## Running
Run: `python -m icd10who_ingest`
