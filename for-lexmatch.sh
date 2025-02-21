#!/bin/bash

# Check if the input file exists
if [ ! -f for-lexmatch.txt ]; then
  echo "File for-lexmatch.txt not found!"
  exit 1
fi

# Loop through each line in the input file
while IFS= read -r ontology; do
  if [ -n "$ontology" ]; then
    echo "Running lexmatch for $ontology..."

    # Run the first command
    poetry run runoak \
      -i nmdc.db \
      -a sqlite:obo:$ontology lexmatch \
      --output nmdc_mixs_vs_${ontology}.SSSOM.tsv \
      i^mixs: @ i^$ontology:

    # Run the second command
    poetry run runoak \
      -i nmdc.db \
      -a sqlite:obo:$ontology lexmatch \
      --output nmdc_nmdc_vs_${ontology}.SSSOM.tsv \
      i^nmdc: @ i^$ontology:
  fi
done < for-lexmatch.txt

echo "All lexmatch operations completed."
