# SNOMED 2 OWL Docker


Wraps the official IHTSDO SNOMED-OWL toolkit: https://github.com/IHTSDO/snomed-owl-toolkit

Example use:

Download the official RF2 files from https://www.nlm.nih.gov/healthit/snomedct/international.html (the following assumes you are allowed to do).

```
SNOMED_VERSION="20200731"
SNOMED_ARCHIVE="MySnomedZip.zip"
docker run -v $PWD/:/work -e SNOMED_VERSION="$SNOMED_VERSION" -e SNOMED_ZIP="$SNOMED_ARCHIVE" --rm -ti ebispot/snomed-owl
```

