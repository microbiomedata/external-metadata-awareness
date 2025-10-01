# onto-intersect
Given two OWL files as input, outputs all the classes and properties they have in common.

It is a strict overlap: it bases what is in common on the IRIs themselves, and the IRIs only. It does not attempt any other kind of matching. For matching on labels and other annotations, use a different tool.

The purpose of this script is purely to find what is exactly shared between two ontologies in terms of classes, object properties, annotation properties, individuals, etc.

The output is two OWL files: a ROBOT extract using a file of CURIEs from the first ontology file, and a ROBOT extract using the same file of CURIEs from the second ontology.

N.B. These two extracts will not necessarily be the same. First, the classes, properties, and even ontologies themselves can have different annotations on them in the two input OWL files. Second, the extract process, as called by the script, preserves the class and property hierachy, which can differ between the two OWL files.

# Setup:
- Follow ROBOT tool installation instructions here: https://robot.obolibrary.org/
- chmod u+x onto-intersect.sh

# Usage:
## If current directory is not in your PATH environment variable
./onto-intersect.sh file-1.owl file-2.owl

## If current directory is in your PATH variable
onto-intersect.sh file-1.owl file-2.owl
