# mixs_preferred_units/

MIxS measurement-slot and unit analysis. **No Python script in this repo
duplicates the UCUM mapping work here**, so these are the canonical record of
that analysis. Related: issue #363 (UCUM alignment), issue #194 (document
measurement analysis), issue #132 (blank preferred-unit annotations).

(Renamed from `mixs_preferred_unts` — fixed typo.)

| Notebook | What it does | Status |
|---|---|---|
| `prefunits_to_ucum.ipynb`, `mixs_preferred_units.ipynb` | Fetch MIxS YAML + a UCUM spreadsheet, explode `preferred_unit` annotations, map to UCUM with a confidence score. | Unique; best productionization candidate. |
| `mine_mixs_for_measurement_slots.ipynb` | Evidence-weighted scoring of measurement slots from live MIxS + NMDC schema. | Overlaps `measurement_discovery_efficient.py` (different approach). |
| `find_unassigned_mixs_slots.ipynb` | MIxS-vs-NMDC slot diff from live YAML. | Overlaps `mixs_slots_in_nmdc.py` (uses TSVs, not live YAML). |
| `ncbi_units_one_hot.ipynb`, `merge_data_counts_and_mappings.ipynb`, `mixs_slot_ranges.ipynb`, `summarize_units_usage_in_mongodb.ipynb` | Unit-token one-hot, data joins, slot-range extraction, MongoDB unit-field counts. | Unique one-offs / utilities. |

**Rerun when:** revisiting MIxS preferred-unit -> UCUM mapping, or refreshing
measurement-slot evidence. `tables/` holds the committed analysis outputs.
