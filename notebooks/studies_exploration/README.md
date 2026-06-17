# studies_exploration/

Per-study notebooks showing how environmental triads (env_broad_scale,
env_local_scale, env_medium) were assessed or re-curated for a specific study,
identifiable by place / person / project. These are kept as worked examples and
as reusable patterns for future studies, not as production pipelines.

| Directory / notebook | Study | What it demonstrates | Rerun when |
|---|---|---|---|
| `emp_500_ng/emp500_ng.ipynb` | EMP500 (bioproject PRJEB42019 / GOLD Gs0154244) | The flagship GOLD-vs-NCBI env-triad re-curation: OAK annotation, biome/ABP/env-material subset validation, obsolete-term replacement, integrating per-sample curations. The test bed for the AI metadata-suggestor tool. | Re-curating EMP500 or validating the suggestor against it. |
| `emp_500_ng/myrold/` | Myrold soil samples (within EMP500) | Land-cover + OSM-assisted env_local_scale inference; cited as the case where suboptimal GOLD curation created duplicate terms. | Applying geospatial inference to a new soil study. |
| `emp_500_ng/MacRae-Crerar/` | MacRae-Crerar samples (within EMP500) | Coordinate-clustering -> inferred ENVO curie/label per biosample. | A study needing per-sample coordinate-based curation. |
| `simons_wishlist/` | Simon Roux (LBL/JGI) SRA import wishlist | Pulling asserted + NER-mined env triads for ~30k biosamples across 113 bioprojects, joined with SRA metadata; feeds NCBI-import work. | Generating/automating an SRA import-candidate sheet. |
| `stream_bank_riparian/` | A real submitter case (via Montana Smith) | Distinguishing stream vs river-bank sediment for env_local_scale when the metadata doesn't say. | Submitter-support env-triad judgment calls. |
| `streams_assessments_llm/` | STREAMS initiative (Julia Kelliher) | LLM assessment of how well stream/river microbiome manuscripts meet reporting standards. See its README. | Re-running the STREAMS reporting-standards assessment. |
| `marie_kroeger_gs0153999/` | GOLD study Gs0153999 (Marie Kroeger) | Single-study ecosystem + ENVO field extraction to TSV. | Extracting one GOLD study's env fields. |
| `predict_env_local_scale_from_nlcd_geotiff.ipynb` | (method) | env_local_scale from an NLCD land-cover raster + ENVO crosswalk. | Geospatial env_local_scale inference. |
| `predict_env_local_scale_from_osm.ipynb` | (method) | env_local_scale from OpenStreetMap/Overpass features near coordinates. | Geospatial env_local_scale inference. |
| `map_with_folium.ipynb` | (utility) | Generic lat/lon TSV -> folium HTML map. | Mapping any biosample coordinate set. |
| `ncbi_annotation_mining/` | (pipeline origin) | Original env-triad mining; see its README (mostly superseded). | Reference / the un-ported algorithms. |
| `flattening/` | (legacy) | Alternative-identifier + legacy biosample flattening; overlaps `flatten_biosample_attributes.py`. | Reference only. |

Provenance for these was confirmed across NMDC Slack (squads `#squad-emp500`,
`#squad-environmental-triad`, `#squad-ncbi-import`, `#squad-ai-metadata-suggestor-tool`)
and shared Google Sheets. All are NMDC-scoped work.
