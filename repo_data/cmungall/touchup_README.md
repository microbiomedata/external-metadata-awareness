# touchup
for keeping the PAINT GAF files up to date

Touchup is used both as a standalone application (for periodic updates), and it is also the backend API for PAINT, which is the curator interface.

Over time any number of changes will be made to the information originally used to annotate the set of proteins in a family

1. The reference proteomes are updated annually and these proteomes are used to build new protein family trees by PANTHER. Consequently ancestral proteins may have added/removed descendants and thus subsequent changes must be made to any propagated descriptions. Ancestral proteins may also move between and within trees, or be lost completely. All of which influence the original annotations.

2. The ontology changes. Terms become deprecated or replaced and thus annotations using those terms must reflect these changes.

3. Primary experimental data is occasionally revised for correcting faulty annotations, therefore any phylogenetically based annotations dependent on these but also be revised

Touchup requires owltools for i) navigating the ontologies, ii) GOlr for retrieving the experimental annotations, and iii) taxon checking see: https://github.com/owlcollab/owltools for details

To build touchup use "mvn clean install"
