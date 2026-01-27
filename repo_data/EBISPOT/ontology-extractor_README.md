README for ChEBI-EFO import script

1) Ensure a copy of the ontology you wish to extract from is available in the imports folder (e.g. chebi.owl)
    - By default, chebi.owl is curled from OLS in the format.sh script. If you wish to change this, simply change the url of the ontology.
    - If you are wanting to extract from a different ontology, you will need to rename all instances of chebi.owl in the format.sh and extract.sh files with your chosen extract ontology.
2) Complete the template file to dictate the terms you wish to extract and their desired parent.
    - The parent term should either be stated in the template file before the child term or be present in EFO currently.
    - ID should be in the CURIE format
    - Parent should also be in the CURIE format
3) Check the extract.sh file contains all of the prefixes needed for your import.
    - For example: If all terms you're extracting and the parent terms are ChEBI terms, then you will only require: --prefix "CHEBI: http://purl.obolibrary.org/obo/CHEBI_"
    - On the other hand, if the extract terms were ChEBI terms but one of the parent terms was an EFO term, you would require: --prefix "CHEBI: http://purl.obolibrary.org/obo/CHEBI_" --prefix "EFO: http://www.ebi.ac.uk/efo/EFO_"
3) Finally, to run the script: bash import.sh
