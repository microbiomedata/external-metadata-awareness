This is the main repository for the BioCADDIE GYM Harvester project

This project will explore the use of social coding sites such as
GitHub for publishing and sharing descriptions of datasets. We will
develop create a format aligned with the Health Care and Life Sciences
(HCLS) Dataset Description profile that can be easily embedded in a
project repository, and foster a lightweight tool ecosystem around
this. This includes dynamic publishing of dataset descriptions, and
automatic validation through the Travis continuous integration
system. We will pilot this project by taking existing datasets and
describing them retrospectively, and by working with an existing
project and describing this prospectively. The goal will to ultimately
have this indexed within the biocaddie system.

## Getting Started

Go to the fake-data demo/template site:

http://biodatasets.github.io/mybiocaddie/

And click "Fork Me", follow the instruction there.

## About this repository

For sharing our data and metadata, follow the instructions above. This
repo houses many of the scripts and tools that take of things behind
the scenes.

### Validation and Processing Scripts

See the [bin](bin) directory for useful scripts for parsing and
aggregating md files.

The mybiocaddie template includes a file [.travis.yml](https://github.com/biodatasets/mybiocaddie/blob/gh-pages/.travis.yml)

Currently this downloads a python script from this repo, and this is
executed to test the contents of the repo. Note: people forking the
mybiocaddie template will need to enable travis to perform checks.

See also [issue 9](https://github.com/cmungall/biocaddie-gym/issues/9)

### Harvesting

See: https://github.com/cmungall/biocaddie-gym/milestone/4

One of the aims of the project is to demonstrate the feasibility of
harvesting user-supplied metadata in github repositories.

The demonstrator function here is not intended to supplant actual
BioCaddie harvesting technologies, but to show how they may be
augmented.

See the [Makefile](Makefile) for how to run this harvesting step.

TODO: [issue 11 make a CI job](https://github.com/cmungall/biocaddie-gym/issues/11)

# Dataset Providers: we want you!

Do you provide or release data using a distributed VCS site like
github? Are you interested in doing this? Alternatively, are you
interested in using github to provide metadata for data released
elsewhere (e.g. Dryad, FigShare, ...)?

If so, we want to hear from you!

Twitter: @biocaddie or @chrismungall
GitHub: @cmungall
Email: cjmungall@lbl.gov

More details coming soon...

