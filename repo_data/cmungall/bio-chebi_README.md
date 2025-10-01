# bio-chebi

NOT YET IN PRODUCTION

This repo will replace the current bio-chebi builds in the GO svn repo - see https://github.com/geneontology/go-ontology/issues/12211

There are two main products:

 * substance-by-role.{obo,owl}
 * bio-chebi.owl

Note these are *NOT* to be deposited in this repository. Instead they will be built by jenkins, deployed on S3/Cloudfront, and made available via purls with the prefix http://purl.obolibrary.org/obo/go/chebi/

## Background

Hill, D. P., Adams, N., Bada, M., Batchelor, C., Berardini, T. Z., Dietze, H., … Lomax, J. (2013). Dovetailing biology and chemistry: integrating the Gene Ontology with the ChEBI chemical ontology. BMC Genomics, 14(1), 513. doi:10.1186/1471-2164-14-513
