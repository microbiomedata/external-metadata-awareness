# Wastewater subtype labeling guide

For the hand-checked set in https://github.com/microbiomedata/external-metadata-awareness/issues/580. Written 2026-10-13, before any sample was read.

Label each BioSample from its own record only: `env_broad_scale`, `env_local_scale`, `env_medium`, `isolation_source`, `description_title` and the sample name. Don't look up the BioProject or paper. A sample can take more than one label.

| label | use when the record says the sample is |
|---|---|
| inflow | untreated sewage at or entering a treatment plant: raw sewage, plant influent, after screening or grit removal, primary influent |
| sewer | taken in the collection system upstream of a plant: sewer pipe, manhole, pumping or lift station, sewershed, sewer biofilm or sediment, building or hospital drain |
| effluent | wastewater after a treatment step: primary, secondary or tertiary effluent, final effluent, reclaimed or reuse water |
| sludge | treatment biomass or solids: activated sludge, mixed liquor, return or waste sludge, granules, carrier biofilm in an aerobic or anoxic reactor, biosolids |
| digester | anaerobic digester contents: digestate, anaerobic digester sludge, biogas or fermentation reactors, including manure and food-waste digesters |
| none | something else: river or lake water (even downstream of a plant), soil, stool, isolates or genomes with no setting, industrial process water, a lab culture |
| unclear | the record is too sparse to choose, such as "wastewater" with nothing else |

Also record:

- `lab_scale`: yes when the record says lab, bench, pilot or a numbered reactor.
- `note`: the phrase that decided it, in a few words.

Rules of thumb:

- "Influent" to a later treatment step, such as ozone influent in a reclamation plant, is effluent of the step before it, so label it effluent.
- Hospital or household wastewater with no place in the system named is sewer.
- "Anaerobic sludge" from a digester is digester. From an anaerobic zone of an activated sludge plant, it is sludge.
