// Purpose: Check how well flow words and tokens in the BioSample sample name agree with flow read from other fields, overall and by BioProject
// Input: wastewater_biosample_candidates (from find_wastewater_biosamples.js), biosamples_flattened, biosamples_ids, biosamples_links, sra_biosamples_bioprojects
// Output: wastewater_flow_labels (replaced by $out; one document per candidate with its flow flags), then a report on stdout
// Related: https://github.com/microbiomedata/external-metadata-awareness/issues/580
//
// mongosh --quiet "$MONGO_URI" mongo-js/wastewater_sample_name_flow_check.js
//
// The patterns are copied from wastewater_bioproject_table.js; keep the two in step.

const INFLOW_TERMS = /(?<!surface water )influent|inflow|in-flow|raw (sewage|wastewater|waste water)|untreated (sewage|wastewater|waste water)|incoming ([a-z-]+ )?(sewage|wastewater|waste water)|plant inlet|\binlet\b/i;
const OUTFLOW_TERMS = /effluent|effulent|\befluent|effleunt|outflow|outfall|(?<!un)treated ([a-z-]+ )?(sewage|wastewater|waste water)(?! ?sludge)|secondary[- ]treated (water|wastewater|waste water|sewage|effluent)|after secondary (treatment|clarifier|clarification)|discharge/i;
const FLOW_FIELDS = ["env_broad_scale", "env_local_scale", "env_medium", "isolation_source", "description_title"];
const MATRIX_INFLOW = /^(raw wastewater|post grit removal)$/i;
const MATRIX_OUTFLOW = /effluent/i;
const NAME_INFLOW_TOKENS = /(^|[^A-Za-z])(IN|INF|INFL|Inf|Infl)([^A-Za-z]|$)/;
const NAME_OUTFLOW_TOKENS = /(^|[^A-Za-z])(EF|EFF|Eff|OUT)([^A-Za-z]|$)/;
const NAME_RAW_TOKENS = /(^|[^A-Za-z])(RAW|Raw|RW)([^A-Za-z]|$)/;

const matches = (f, re) => ({ $regexMatch: { input: { $toString: { $ifNull: [`$${f}`, ""] } }, regex: re } });
const anyField = (re) => ({ $or: FLOW_FIELDS.map(f => matches(f, re)) });

// The lookups below need these; the flattening scripts do not create them. Skip any that already exist under another name.
const ensureIndex = (coll, key) => {
  const k = JSON.stringify(key);
  if (!coll.getIndexes().some(i => JSON.stringify(i.key) === k)) coll.createIndex(key);
};
ensureIndex(db.biosamples_flattened, { accession: 1 });
ensureIndex(db.biosamples_ids, { accession: 1 });
ensureIndex(db.biosamples_links, { target: 1, accession: 1 });
ensureIndex(db.sra_biosamples_bioprojects, { biosample_accession: 1 });

db.wastewater_biosample_candidates.aggregate([
  { $project: Object.assign({ _id: 0, accession: 1 }, Object.fromEntries(FLOW_FIELDS.map(f => [f, 1]))) },
  { $lookup: { from: "biosamples_flattened", localField: "accession", foreignField: "accession", pipeline: [{ $project: { _id: 0, ww_sample_matrix: 1 } }], as: "flat" } },
  { $lookup: { from: "biosamples_ids", localField: "accession", foreignField: "accession", pipeline: [{ $match: { label: "Sample name" } }, { $project: { _id: 0, content: 1 } }], as: "ids" } },
  { $lookup: { from: "biosamples_links", let: { acc: "$accession" }, pipeline: [{ $match: { $expr: { $and: [{ $eq: ["$target", "bioproject"] }, { $eq: ["$accession", "$$acc"] }] } } }, { $project: { _id: 0, label: 1 } }], as: "bp_links" } },
  { $lookup: { from: "sra_biosamples_bioprojects", localField: "accession", foreignField: "biosample_accession", as: "bp_sra" } },
  {
    $addFields: {
      ww_sample_matrix: { $arrayElemAt: ["$flat.ww_sample_matrix", 0] },
      sample_name: { $ifNull: [{ $arrayElemAt: ["$ids.content", 0] }, ""] },
      bioprojects: { $cond: [{ $gt: [{ $size: "$bp_links" }, 0] }, { $setUnion: ["$bp_links.label"] }, { $setUnion: ["$bp_sra.bioproject_accession"] }] }
    }
  },
  {
    $project: {
      accession: 1, sample_name: 1, bioprojects: 1,
      field_inflow: { $or: [matches("ww_sample_matrix", MATRIX_INFLOW), anyField(INFLOW_TERMS)] },
      field_outflow: { $or: [matches("ww_sample_matrix", MATRIX_OUTFLOW), anyField(OUTFLOW_TERMS)] },
      name_inflow_words: matches("sample_name", INFLOW_TERMS),
      name_inflow_tokens: matches("sample_name", NAME_INFLOW_TOKENS),
      name_outflow_words: matches("sample_name", OUTFLOW_TERMS),
      name_outflow_tokens: matches("sample_name", NAME_OUTFLOW_TOKENS),
      name_raw_tokens: matches("sample_name", NAME_RAW_TOKENS)
    }
  },
  { $out: "wastewater_flow_labels" }
], { allowDiskUse: true });

const L = db.wastewater_flow_labels;
print(`candidates: ${L.countDocuments()}, with a sample name: ${L.countDocuments({ sample_name: { $ne: "" } })}`);

// For each sample-name rule: agree = the fields say the same flow, disagree = the fields say only the other flow, new = the fields say neither
const RULES = [
  ["inflow tokens", "name_inflow_tokens", "field_inflow", "field_outflow"],
  ["inflow words", "name_inflow_words", "field_inflow", "field_outflow"],
  ["RAW tokens (not used)", "name_raw_tokens", "field_inflow", "field_outflow"],
  ["outflow tokens", "name_outflow_tokens", "field_outflow", "field_inflow"],
  ["outflow words", "name_outflow_words", "field_outflow", "field_inflow"]
];
const pct = (a, b) => (b ? (100 * a / b).toFixed(1) : "");

print("\n== overall and by BioProject");
print(["rule", "agree", "disagree", "new", "agreement %", "BioProjects with agree or disagree", "share of agree from largest project %", "agreement % without largest project", "median project agreement %"].join("\t"));
RULES.forEach(([label, rule, same, other]) => {
  const tot = L.aggregate([
    { $match: { [rule]: true } },
    { $group: { _id: null, agree: { $sum: { $cond: [`$${same}`, 1, 0] } }, disagree: { $sum: { $cond: [{ $and: [`$${other}`, { $not: [`$${same}`] }] }, 1, 0] } }, neither: { $sum: { $cond: [{ $or: [`$${same}`, `$${other}`] }, 0, 1] } } } }
  ]).toArray()[0] || { agree: 0, disagree: 0, neither: 0 };
  // A sample in several BioProjects counts in each. Samples with no BioProject are grouped as "(none)" and kept out of the project statistics.
  const grouped = L.aggregate([
    { $match: { [rule]: true, $or: [{ [same]: true }, { [other]: true }] } },
    { $unwind: { path: "$bioprojects", preserveNullAndEmptyArrays: true } },
    { $group: { _id: { $ifNull: ["$bioprojects", "(none)"] }, agree: { $sum: { $cond: [`$${same}`, 1, 0] } }, disagree: { $sum: { $cond: [{ $not: [`$${same}`] }, 1, 0] } } } },
    { $sort: { agree: -1, _id: 1 } }
  ], { allowDiskUse: true }).toArray();
  const none = grouped.find(d => d._id === "(none)") || { agree: 0, disagree: 0 };
  const byBp = grouped.filter(d => d._id !== "(none)");
  const sumAgree = byBp.reduce((s, d) => s + d.agree, 0);
  const top = byBp[0] || { agree: 0, disagree: 0 };
  const rest = byBp.slice(1);
  const restAgree = rest.reduce((s, d) => s + d.agree, 0), restDis = rest.reduce((s, d) => s + d.disagree, 0);
  const perProject = byBp.filter(d => d.agree + d.disagree >= 5).map(d => d.agree / (d.agree + d.disagree)).sort((a, b) => a - b);
  const mid = Math.floor(perProject.length / 2);
  const median = !perProject.length ? "" :
    (100 * (perProject.length % 2 ? perProject[mid] : (perProject[mid - 1] + perProject[mid]) / 2)).toFixed(1);
  print([label, tot.agree, tot.disagree, tot.neither, pct(tot.agree, tot.agree + tot.disagree), byBp.length,
    pct(top.agree, sumAgree), pct(restAgree, restAgree + restDis), median].join("\t"));
  print(`  largest: ${top._id} (${top.agree} agree, ${top.disagree} disagree); projects with a disagreement: ` +
    byBp.filter(d => d.disagree > 0).sort((a, b) => b.disagree - a.disagree || String(a._id).localeCompare(String(b._id))).slice(0, 5).map(d => `${d._id} ${d.disagree}/${d.agree + d.disagree}`).join(", ") +
    `; no BioProject: ${none.agree} agree, ${none.disagree} disagree`);
});
