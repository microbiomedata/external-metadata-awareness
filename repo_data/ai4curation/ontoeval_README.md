# ontobench

This repo has code for creating benchmarks for ontology changes.

For each pull request:

- fetch metadata from github
- find linked issue(s)
- fetch the commit IDs of the "before" and "after" states
- create a diff/patch from the two IDs

All of this information will be stored in a pydantic data model, and exported to JSON

Note that commits are typically simple changes in the *-edit.obo file, but may involve other files

See workdir/ for some example repos that are checked out.


Examples

go-ontology

* 13117 - multiple stanzas