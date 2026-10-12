// Purpose: Summarize wastewater candidate biosamples by BioProject, so a subset can be picked by whole project
// Input: wastewater_biosample_candidates (from find_wastewater_biosamples.js), biosamples_links, sra_biosamples_bioprojects, bioprojects_flattened,
//        and optionally mgnify_wastewater_samples (one document per MGnify sample, field accession = BioSample accession)
// Output: wastewater_bioproject_summary (replaced by $out), then one TSV row per BioProject on stdout
// Related: https://github.com/microbiomedata/external-metadata-awareness/issues/570
//
// mongosh --quiet "$MONGO_URI" mongo-js/wastewater_bioproject_table.js > wastewater_bioprojects.tsv

const CORE_TERMS = /wast[e]?[ -]?water|sewage|sewer|wwtp|activated[ -]?sludge/i;
const OLD_CORE_TERMS = /wast[e]?[ -]?water|sewage|sewer|wwtp/i;
const FIELDS = [
  "package_content", "env_package", "taxonomy_name",
  "env_broad_scale", "env_local_scale", "env_medium",
  "isolation_source", "description_title"
];
// BioProjects curated in https://github.com/cmungall/site-kb (db/raw/research/wastewater_expansion_ena.json, retrieved 2026-09-23)
const SITE_KB = ["PRJNA1012295", "PRJNA1149857", "PRJNA432264", "PRJNA1037153", "PRJNA505617"];

const anyField = re => ({ $or: FIELDS.map(f => ({ $regexMatch: { input: { $ifNull: [`$${f}`, ""] }, regex: re } })) });
const flag = cond => ({ $sum: { $cond: [cond, 1, 0] } });
const hasMgnify = db.getCollectionNames().includes("mgnify_wastewater_samples");

// The lookups below need these; the flattening scripts do not create them. Skip any that already exist under another name.
const ensureIndex = (coll, key) => {
  const k = JSON.stringify(key);
  if (!coll.getIndexes().some(i => JSON.stringify(i.key) === k)) coll.createIndex(key);
};
ensureIndex(db.biosamples_links, { target: 1, accession: 1 });
ensureIndex(db.sra_biosamples_bioprojects, { biosample_accession: 1 });
ensureIndex(db.bioprojects_flattened, { accession: 1 });
if (hasMgnify) ensureIndex(db.mgnify_wastewater_samples, { accession: 1 });

db.wastewater_biosample_candidates.aggregate([
  { $project: Object.assign({ accession: 1, owner_name: 1, geo_loc_name: 1 }, Object.fromEntries(FIELDS.map(f => [f, 1]))) },
  {
    $lookup: {
      from: "biosamples_links",
      let: { acc: "$accession" },
      pipeline: [
        { $match: { $expr: { $and: [{ $eq: ["$target", "bioproject"] }, { $eq: ["$accession", "$$acc"] }] } } },
        { $project: { _id: 0, label: 1 } }
      ],
      as: "bp_links"
    }
  },
  // EBI biosamples (SAMEA) often have no BioProject link in the BioSample record; fall back to the SRA run table
  { $lookup: { from: "sra_biosamples_bioprojects", localField: "accession", foreignField: "biosample_accession", as: "bp_sra" } },
  {
    $addFields: {
      bp: {
        $cond: [
          { $gt: [{ $size: "$bp_links" }, 0] },
          { $setUnion: ["$bp_links.label"] },
          { $setUnion: ["$bp_sra.bioproject_accession"] }
        ]
      },
      bp_source: { $cond: [{ $gt: [{ $size: "$bp_links" }, 0] }, "biosample", { $cond: [{ $gt: [{ $size: "$bp_sra" }, 0] }, "sra", "none"] }] }
    }
  },
  ...(hasMgnify ? [{ $lookup: { from: "mgnify_wastewater_samples", localField: "accession", foreignField: "accession", as: "mg" } }] : []),
  {
    $addFields: {
      core: anyField(CORE_TERMS),
      old_core: anyField(OLD_CORE_TERMS),
      mixs_pkg: { $regexMatch: { input: { $ifNull: ["$package_content", ""] }, regex: /wastewater/ } },
      wwsurv_pkg: { $regexMatch: { input: { $ifNull: ["$package_content", ""] }, regex: /wwsurv/ } },
      in_mgnify: { $gt: [{ $size: { $ifNull: ["$mg", []] } }, 0] },
      country: { $trim: { input: { $arrayElemAt: [{ $split: [{ $ifNull: ["$geo_loc_name", ""] }, ":"] }, 0] } } },
      n_bioprojects: { $size: "$bp" }
    }
  },
  // A biosample linked to several BioProjects is counted under each, so every row shows that project's full membership
  { $unwind: { path: "$bp", preserveNullAndEmptyArrays: true } },
  { $addFields: { bioproject: { $ifNull: ["$bp", "(no BioProject link)"] } } },
  {
    $group: {
      _id: "$bioproject",
      biosamples: { $sum: 1 },
      wastewater: flag("$core"),
      activated_sludge_only: flag({ $and: ["$core", { $not: ["$old_core"] }] }),
      adjacent_only: flag({ $not: ["$core"] }),
      mixs_wastewater_package: flag({ $and: ["$core", "$mixs_pkg"] }),
      wwsurv_package: flag({ $and: ["$core", "$wwsurv_pkg"] }),
      in_mgnify: flag("$in_mgnify"),
      linked_to_several_bioprojects: flag({ $gt: ["$n_bioprojects", 1] }),
      bioproject_from_sra_runs: flag({ $eq: ["$bp_source", "sra"] }),
      owners: { $addToSet: "$owner_name" },
      countries: { $addToSet: "$country" },
      packages: { $addToSet: "$package_content" }
    }
  },
  { $lookup: { from: "bioprojects_flattened", localField: "_id", foreignField: "accession", as: "p" } },
  {
    $project: {
      _id: 0,
      bioproject: "$_id",
      title: { $ifNull: [{ $arrayElemAt: ["$p.title", 0] }, { $arrayElemAt: ["$p.name", 0] }] },
      biosamples: 1, wastewater: 1, activated_sludge_only: 1, adjacent_only: 1,
      mixs_wastewater_package: 1, wwsurv_package: 1, in_mgnify: 1, linked_to_several_bioprojects: 1, bioproject_from_sra_runs: 1,
      in_site_kb: { $in: ["$_id", SITE_KB] },
      owners: 1, countries: 1, packages: 1
    }
  },
  { $sort: { wastewater: -1, biosamples: -1 } },
  { $out: "wastewater_bioproject_summary" }
], { allowDiskUse: true });

// Quote a field that contains a double quote, doubling the quotes, so quote-aware TSV readers keep every row
const clean = s => {
  const v = s === null || s === undefined ? "" : String(s).replace(/[\t\r\n]+/g, " ").trim();
  return v.includes('"') ? `"${v.replace(/"/g, '""')}"` : v;
};
const list = a => (a || []).filter(x => x).sort().join("; ");
const cols = ["bioproject", "title", "biosamples", "wastewater", "activated_sludge_only", "adjacent_only",
  "mixs_wastewater_package", "wwsurv_package", "in_mgnify", "in_site_kb", "linked_to_several_bioprojects", "bioproject_from_sra_runs",
  "owners", "countries", "packages"];
print(cols.join("\t"));
db.wastewater_bioproject_summary.find().sort({ wastewater: -1, biosamples: -1 }).forEach(d =>
  print(cols.map(c => (Array.isArray(d[c]) ? clean(list(d[c])) : clean(d[c]))).join("\t")));
