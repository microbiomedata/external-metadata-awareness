# id_sandbox
A place for trying out NMDC identifier principles

Relevant resources:
- newer [automated combined_classes_slots_minimal_filtered](https://docs.google.com/spreadsheets/d/19OOuavI--G8zXidiobr41U1dBGEQK8GNVvDrPejtT7s/edit#gid=1982139992)
- older but more recerntly curated [Identifiers_Map Identifiers Flow](https://docs.google.com/spreadsheets/d/1e7hA0H4lkkHCNjYxMSkTR3BrYI3Jp-lJsnfOGyK28L8/edit#gid=2091302437)


---

* id_sandbox/tidy_combined.py (for tagging identifying and naming slots) doesn't tag anything containing just "ident" or "taxid", without meeting some other criterion.
* I'm not sure whether case variants are matched yet.
* But qualitatively, the tagged (and untagged) slots look good to me.
* The all-classes relevant to slot functionality hasn't been implemented yet.
* A slot may appear on several lines
* could add more attributes to the report, like description, multivalued, required, identifier, etc.
  * displaying more attributes isn't the same as using them to determine whether a slot is a namer or an identifier, but that could be added too
* Need to call out the identifiers used for biosamples and studies by MongoDB
