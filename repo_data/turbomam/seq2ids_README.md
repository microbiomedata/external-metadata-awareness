# seq2ids
BLAST sequences to get ids for taxon, gene, protein, enzyme, etc.

Currently focusing on BLASTXs against Uniprot. (Remember, NCBI still calls the corresponding BLAST database "swissprot".)

Can be applied to detection of genetic engineering, but requires that the nt sequences of the modifications are available.

Types of modifications considered:

- deletion flanks (no special handling yet)
- deletions
- insertions
- sequences (not sure what that means)

