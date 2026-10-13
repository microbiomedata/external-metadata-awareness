// Purpose: Collect biosamples that mention wastewater, or an adjacent term, in any of eight fields, without relying on the NCBI package
// Input: biosamples_flattened (~56M docs)
// Output: wastewater_biosample_candidates (~579K docs, replaced by $out). About 4 minutes on the M5.
// Related: https://github.com/microbiomedata/external-metadata-awareness/issues/570
//
// Core and adjacent terms are split later by report_wastewater_biosamples.js.

const TERMS = /wast[e]?[ -]?water|sewage|sewer|sludge|wwtp|effluent|influent|digester|biosolid/i;
const FIELDS = [
  "package_content", "env_package", "taxonomy_name",
  "env_broad_scale", "env_local_scale", "env_medium",
  "isolation_source", "description_title"
];

const started = new Date();
db.biosamples_flattened.aggregate([
  { $match: { $or: FIELDS.map(f => ({ [f]: TERMS })) } },
  {
    $project: Object.assign(
      { accession: 1, taxonomy_id: 1, geo_loc_name: 1, collection_date: 1, host: 1, owner_name: 1 },
      Object.fromEntries(FIELDS.map(f => [f, 1]))
    )
  },
  { $out: "wastewater_biosample_candidates" }
], { allowDiskUse: true });

print(`Created wastewater_biosample_candidates with ${db.wastewater_biosample_candidates.countDocuments()} documents in ${(new Date() - started) / 1000} s`);
