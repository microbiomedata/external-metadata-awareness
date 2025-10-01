# Replicant
Tools for generating simulated rare-disease VCF and associated phenotypes

replicant/ˈrɛplɪk(ə)nt/ _n._ a genetically engineered or artificial being created as an exact replica of a particular human being.

# Aim
When creating tools for use in NGS diagnostics such as the [Exomiser](github.com/exomiser/Exomiser) it becomes problematic when searching for a benchmarking set required to test the software on as real genomic data from real patients is not publically available. This is problematic for benchmarking individual software packages although it is possible to overcome this by working in collaboration with a rare-disease programme such as the UDN, UDP, 100KGenomes, DDD, Care 4 Rare etc. The problem comes when trying to compare different software packages on identical datasets because there are no publically available datasets for benchmarking purposes. Another issue is that even if a rare disease dataset is available for testing against, the dataset might have a syndrome bias. This package aims to solve these problems. 
