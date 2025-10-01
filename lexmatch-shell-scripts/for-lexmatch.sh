#!/bin/bash

# ==============================================================================
# Batch Lexical Matching for Ontology Alignment
# ==============================================================================
#
# PURPOSE:
#   Performs batch lexical matching between NMDC/MIxS terms and multiple
#   ontologies using OAK (Ontology Access Kit) to generate SSSOM mapping files
#   for semantic alignment research.
#
# USAGE:
#   ./for-lexmatch.sh
#
# PREREQUISITES:
#   - for-lexmatch.txt: Text file containing one ontology name per line (e.g., "envo", "chebi")
#   - nmdc.db: SQLite database containing NMDC schema terms
#   - env_triad_pvs_sheet.db: Environmental triad permissible values database
#   - poetry environment with OAK installed
#   - ../lexmatch-output/ directory for output files
#
# INPUT FILE FORMAT (for-lexmatch.txt):
#   envo
#   chebi
#   go
#   ...
#
# OUTPUTS:
#   - ../lexmatch-output/nmdc_mixs_vs_${ontology}.SSSOM.tsv: MIxS term mappings
#   - ../lexmatch-output/nmdc_nmdc_vs_${ontology}.SSSOM.tsv: NMDC term mappings
#   - ../lexmatch-output/env_triad_pvs_vs_${ontology}.SSSOM.tsv: Environmental triad mappings
#   - lexmatch-errors.txt: Error log from all operations
#
# NORMALIZATION STEPS:
#   - Case normalization (lowercase)
#   - Whitespace normalization (trim/collapse)
#   - Word order normalization (alphabetical)
#
# ==============================================================================

# Check if the input file exists
if [ ! -f for-lexmatch.txt ]; then
  echo "File for-lexmatch.txt not found!"
  exit 1
fi

rm -rf lexmatch-errors.txt
#rm -rf lexmatch-output/*

# Loop through each line in the input file
while IFS= read -r ontology; do
  if [ -n "$ontology" ]; then

    echo "nmdc mixs vs $ontology"
    poetry run runoak \
      -i nmdc.db \
      -a sqlite:obo:$ontology \
      lexmatch \
      --add-pipeline-step CaseNormalization \
      --add-pipeline-step WhitespaceNormalization  \
      --add-pipeline-step WordOrderNormalization \
      --output ../lexmatch-output/nmdc_mixs_vs_${ontology}.SSSOM.tsv \
      i^mixs @ .all \
      2>>lexmatch-errors.txt

    echo "nmdc nmdc vs $ontology"
    poetry run runoak \
      -i nmdc.db \
      -a sqlite:obo:$ontology \
      lexmatch \
      --add-pipeline-step CaseNormalization \
      --add-pipeline-step WhitespaceNormalization  \
      --add-pipeline-step WordOrderNormalization \
      --output ../lexmatch-output/nmdc_nmdc_vs_${ontology}.SSSOM.tsv \
      i^nmdc @ .all \
      2>>lexmatch-errors.txt

#    echo "submission schema vs $ontology"
#    poetry run runoak \
#      -i nmdc_submission_schema_no_from_schema_no_brackets.db \
#      -a sqlite:obo:$ontology \
#      lexmatch \
#      --add-pipeline-step CaseNormalization \
#      --add-pipeline-step WhitespaceNormalization  \
#      --add-pipeline-step WordOrderNormalization \
#      --output lexmatch-output/submission_schema_vs_${ontology}.SSSOM.tsv \
#      i^nmdc_sub_schema @ .all \
#      2>>lexmatch-errors.txt


    echo "env triad PVs vs $ontology"
    poetry run runoak \
      -i env_triad_pvs_sheet.db \
      -a sqlite:obo:$ontology \
      lexmatch \
      --add-pipeline-step CaseNormalization \
      --add-pipeline-step WhitespaceNormalization  \
      --add-pipeline-step WordOrderNormalization \
      --output ../lexmatch-output/env_triad_pvs_vs_${ontology}.SSSOM.tsv \
      i^nmdc_sub_schema @ .all \
      2>>lexmatch-errors.txt
  fi
done < for-lexmatch.txt

echo "All lexmatch operations completed."
