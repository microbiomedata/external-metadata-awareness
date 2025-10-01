# Monarch Ontology stats for RPPR

To generate the RPPR stats, you should have ROBOT or ODK installed.

0. Open the `Makefile` in a text editor and make sure the grant dates are set correctly:
```
START_DATE_P1=2022-08-01
END_DATE_P1=2023-05-31
START_DATE_HPO=2022-07-01
END_DATE_HPO=2023-06-30
```
1. If you are not using ODK, create a new python environment
2. Install requirements.txt (`pip install -r requirements.txt`)
3. Run `make all` (if you run it for the first time in a while, add `-B`, ie. `make all -B`)
4. Push the generated changes to GitHub

