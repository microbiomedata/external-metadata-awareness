#!/bin/bash

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

#    echo "nmdc mixs vs $ontology"
#    poetry run runoak \
#      -i nmdc.db \
#      -a sqlite:obo:$ontology \
#      lexmatch \
#      --add-pipeline-step CaseNormalization \
#      --add-pipeline-step WhitespaceNormalization  \
#      --add-pipeline-step WordOrderNormalization \
#      --output lexmatch-output/nmdc_mixs_vs_${ontology}.SSSOM.tsv \
#      i^mixs @ .all \
#      2>>lexmatch-errors.txt
#
#    echo "nmdc nmdc vs $ontology"
#    poetry run runoak \
#      -i nmdc.db \
#      -a sqlite:obo:$ontology \
#      lexmatch \
#      --add-pipeline-step CaseNormalization \
#      --add-pipeline-step WhitespaceNormalization  \
#      --add-pipeline-step WordOrderNormalization \
#      --output lexmatch-output/nmdc_nmdc_vs_${ontology}.SSSOM.tsv \
#      i^nmdc @ .all \
#      2>>lexmatch-errors.txt
#
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
      --output lexmatch-output/env_triad_pvs_vs_${ontology}.SSSOM.tsv \
      i^nmdc_sub_schema @ .all \
      2>>lexmatch-errors.txt
  fi
done < for-lexmatch.txt

echo "All lexmatch operations completed."
