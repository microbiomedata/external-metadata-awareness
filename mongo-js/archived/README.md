# Archived MongoDB Scripts

This directory contains old/superseded MongoDB scripts kept for historical reference.

## Archived Scripts

### count_biosamples_per_harmonized_name.js
**Status**: Superseded by atomic workflow
**Replacement**: `count_biosamples_per_hn_step[1-3].js`
**Reason**: Monolithic script that runs all steps in one execution. Superseded by atomic, resumable 3-step workflow.
**Date archived**: 2025-10-13
**Related issues**: #235, #268

### count_biosamples_per_harmonized_name_fixed.js
**Status**: Superseded by atomic workflow
**Replacement**: `count_biosamples_per_hn_step[1-3].js`
**Reason**: Fixed version of monolithic script (using `db.getSiblingDB()`). Still monolithic - superseded by atomic workflow.
**Date archived**: 2025-10-13
**Related issues**: #235, #268

## Current Workflow

Use the atomic 3-step workflow instead:

```bash
make -f Makefiles/measurement_discovery.Makefile count-biosamples-per-harmonized-name-atomic
```

Or run steps individually:
1. `count-biosamples-per-hn-step1` - Dedupe and count biosamples
2. `count-biosamples-per-hn-step2` - Count totals and unit coverage
3. `count-biosamples-per-hn-step3` - Join temps and create final collection

Each step is resumable and checks for existing output before running.
