// Purpose: Print the counts behind docs/wastewater-biosamples.md: per-field recall, packages, env field values, curation problems
// Input: wastewater_biosample_candidates (from find_wastewater_biosamples.js)
// Output: stdout only; writes nothing
// Related: https://github.com/microbiomedata/external-metadata-awareness/issues/570

const c = db.wastewater_biosample_candidates;
const CORE_TERMS = /wast[e]?[ -]?water|sewage|sewer|wwtp|activated[ -]?sludge/i;
const WW_PACKAGE = /wastewater|wwsurv/;
const FIELDS = [
  "package_content", "env_package", "taxonomy_name",
  "env_broad_scale", "env_local_scale", "env_medium",
  "isolation_source", "description_title"
];
const ENV_FIELDS = ["env_broad_scale", "env_local_scale", "env_medium"];
const PLACEHOLDER = /^(missing|not applicable|not collected|not provided|na|n\/a|none|unknown|-|restricted access)$/i;
const CORE = { $or: FIELDS.map(f => ({ [f]: CORE_TERMS })) };
const and = q => ({ $and: [CORE, q] });

const top = (field, match, n = 25) => {
  print(`\n== top ${field}`);
  c.aggregate([
    { $match: match },
    { $group: { _id: `$${field}`, n: { $sum: 1 } } },
    { $sort: { n: -1 } },
    { $limit: n }
  ], { allowDiskUse: true }).forEach(d => print(`${d.n}\t${JSON.stringify(d._id)}`));
};

print(`candidates, core or adjacent: ${c.countDocuments()}`);
print(`core: ${c.countDocuments(CORE)}`);
print(`adjacent only: ${c.countDocuments({ $nor: CORE.$or })}`);
print(`core, MIxS wastewater package: ${c.countDocuments(and({ package_content: /wastewater/ }))}`);
print(`core, wwsurv package: ${c.countDocuments(and({ package_content: /wwsurv/ }))}`);
print(`core, no wastewater package: ${c.countDocuments(and({ package_content: { $not: WW_PACKAGE } }))}`);

// How many core samples each field alone would find, and how many only that field finds
const hit = f => ({ $cond: [{ $regexMatch: { input: { $ifNull: [`$${f}`, ""] }, regex: CORE_TERMS } }, 1, 0] });
const group = { _id: null };
FIELDS.forEach(f => {
  group[`hit_${f}`] = { $sum: `$h_${f}` };
  group[`only_${f}`] = { $sum: { $cond: [{ $and: [{ $eq: [`$h_${f}`, 1] }, { $eq: [{ $add: FIELDS.map(x => `$h_${x}`) }, 1] }] }, 1, 0] } };
});
print("\n== per-field hits and sole finds among core samples");
printjson(c.aggregate([
  { $match: CORE },
  { $project: Object.fromEntries(FIELDS.map(f => [`h_${f}`, hit(f)])) },
  { $group: group }
], { allowDiskUse: true }).toArray()[0]);

["package_content", "taxonomy_name", ...ENV_FIELDS, "isolation_source", "owner_name"].forEach(f => top(f, CORE));
top("taxonomy_name", { $nor: CORE.$or }, 12);

print("\n== env fields among core samples");
ENV_FIELDS.forEach(f => print(`${f}: distinct ${c.distinct(f, CORE).length}, absent ${c.countDocuments(and({ [f]: { $exists: false } }))}, placeholder ${c.countDocuments(and({ [f]: PLACEHOLDER }))}, has ENVO id ${c.countDocuments(and({ [f]: /ENVO[:_]\d+/i }))}`));
print(`wwsurv package with no env_broad_scale: ${c.countDocuments(and({ package_content: /wwsurv/, env_broad_scale: null }))} of ${c.countDocuments(and({ package_content: /wwsurv/ }))}`);
print(`MIxS wastewater package with ENVO id in env_medium: ${c.countDocuments(and({ package_content: /wastewater/, env_medium: /ENVO[:_]\d+/i }))} of ${c.countDocuments(and({ package_content: /wastewater/ }))}`);

print("\n== spellings of isolation_source that are only the word wastewater");
top("isolation_source", { isolation_source: /^\s*wast[e]?[ -]?water\s*$/i }, 10);

print("\n== core by country (geo_loc_name before the colon)");
c.aggregate([
  { $match: CORE },
  { $group: { _id: { $arrayElemAt: [{ $split: [{ $ifNull: ["$geo_loc_name", "(none)"] }, ":"] }, 0] }, n: { $sum: 1 } } },
  { $sort: { n: -1 } },
  { $limit: 15 }
]).forEach(d => print(`${d.n}\t${d._id}`));

print("\n== 25 random core samples outside any wastewater package, for a precision check by eye");
c.aggregate([
  { $match: and({ package_content: { $not: WW_PACKAGE } }) },
  { $sample: { size: 25 } },
  { $project: Object.assign({ _id: 0, accession: 1 }, Object.fromEntries(FIELDS.map(f => [f, 1]))) }
]).forEach(d => print(JSON.stringify(d)));
