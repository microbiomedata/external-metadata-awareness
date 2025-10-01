# dh_testing
Sandbox for testing the content of various [LinkML](https://linkml.io/) schema features against [DataHarmonizer](https://github.com/cidgoh/DataHarmonizer)

Motivated by
- https://github.com/microbiomedata/sheets_and_friends/issues/46
- https://github.com/microbiomedata/sheets_and_friends/issues/105
  - https://github.com/microbiomedata/sheets_and_friends/issues/104
    - MAM: check pipeline for converting NMDC/MIxS class (not type) ranges into patterns (via structured patterns) and then using the patterns to validate DataHarmonizer input
    - see also https://github.com/microbiomedata/sheets_and_friends/pull/115
- https://github.com/microbiomedata/sheets_and_friends/issues/107
  - Several efforts underway to improve pipeline for retrieving EnvO and Uberon terms from public sources, providing a way for subject-matter experts to curate the retrieved lists, and then injecting per-environment enumerations for each of the MIxS environmental triad slots. **MAM: elaborate**.
    - see also https://github.com/microbiomedata/sheets_and_friends/issues/133
    - **MAM add more links**

Looking good:
- https://github.com/microbiomedata/sheets_and_friends/issues/106 (DH help screens)

MAM: get a better understanding of how DH interfaces are built and deployed to the NMDC submission portal now. May not involve GitHub pages anymore (so checking and sharing dev builds can probably be done with GH pages, instead of Netlify). This repo uses `gen-linkml --format json` to generate the JSON for the DH interface, not `script/linkml.py`. Then the DH web content can be served locally or packaged up with `yarn dev` and webpack. I believe the dependence on using DH as a git submodule will be removed eventually. The consequences of that need to be documented, too. 

Therefore, most of these are at least mostly irrelevant now:
- https://github.com/microbiomedata/sheets_and_friends/issues/108
- https://github.com/microbiomedata/sheets_and_friends/issues/111
- https://github.com/microbiomedata/sheets_and_friends/issues/114

Note that there are differences between DH's XXX and LinkML's sheets2linkml. Might be an opportunity for improving sheets2linkml.

## Google Sheets Observations
- All non-string cells in a Google Sheet intended for schemasheets must be protected as string with an initial `'`. For example, integers, floats, booleans, dates
- Make sure sheets don't have any merged cells
- linkml minimum_value and maximum_value must be integers, not floats
  - what can't a *_value be a float? LinkML issue? 

## TODOs

- probably skip generating docs with gen-project, unless it's using gen-docs under the hood (ie don't bother with gen-markdown)
- ValueError: File "<file>", line 254, col 15 Unrecognized ifabsent action for slot 'test_ifabsent': 'replacement string'
  - slot_uri works. learn how to use a string
- subsets not getting directly generated from dh_testing sheets? See examples examples 
- define test_any_of_enums in sheets?
- define test_any_of_enums in sheets?
- define test_structured_pattern in sheets
- structured pattern doesn't seem to be working

