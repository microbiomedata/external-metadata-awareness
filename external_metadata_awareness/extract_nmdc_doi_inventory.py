"""Extract all DOI/PMID/URL literature references from a local NMDC MongoDB."""

import csv
import re
import sys
from collections import Counter

import click
from pymongo import uri_parser

from external_metadata_awareness.mongodb_connection import get_mongo_client

DOI_PATTERN = re.compile(r'(?:doi:|https?://doi\.org/|https?://dx\.doi\.org/)?10\.\d{2,9}/[^\s,;\]}"\']+')
PMID_PATTERN = re.compile(r'PMID[:\s]*(\d+)', re.IGNORECASE)

BIOSAMPLE_FIELDS = [
    "chem_administration", "nucl_acid_amp", "nucl_acid_ext", "host_growth_cond",
    "soil_org_carb_meth", "soil_org_nitro_meth", "soil_texture_meth",
    "micro_biomass_c_meth", "micro_biomass_meth", "micro_biomass_n_meth",
    "ph_meth", "water_cont_soil_meth", "soil_type_meth", "dna_isolate_meth",
    "samp_collec_method", "biotic_regm", "cur_vegetation", "description",
    "source_mat_id", "host_diet", "perturbation", "experimental_factor",
    "experimental_factor_other", "other_treatment", "store_cond",
    "cult_root_med", "ances_data", "misc_param",
]

OTHER_COLLECTIONS = [
    "data_generation_set", "workflow_execution_set", "material_processing_set",
    "processed_sample_set", "calibration_set", "configuration_set",
    "data_object_set", "field_research_site_set",
]


def clean_doi(ref):
    """Normalize to doi:10.xxx form and strip trailing punctuation."""
    m = re.search(r'(10\.\d{2,9}/[^\s,;\]}"\']+)', ref)
    if m:
        val = m.group(1)
        val = val.rstrip(".]}'\">/")
        while val.endswith(")") and val.count(")") > val.count("("):
            val = val[:-1]
        return "doi:" + val
    return ref


def get_raw_str(val):
    """Get the string that should be searched for DOIs."""
    if isinstance(val, str):
        return val
    elif isinstance(val, dict):
        raw = val.get("has_raw_value", "")
        return raw if raw else str(val)
    elif isinstance(val, list):
        return "; ".join(get_raw_str(v) for v in val)
    return str(val)


def is_sole_doi(raw_str, doi_match):
    """Check if the DOI constitutes the entire field value (not embedded in text)."""
    stripped = raw_str.strip()
    doi_only = re.compile(
        r'^(?:doi:|https?://(?:dx\.)?doi\.org/)?10\.\d{2,9}/[^\s]+$'
    )
    return bool(doi_only.match(stripped))


def extract_refs_with_context(val):
    """Extract DOI and PMID references, plus the raw string for sole-value check."""
    if val is None:
        return []
    if isinstance(val, list):
        results = []
        for item in val:
            results.extend(extract_refs_with_context(item))
        return results

    raw_str = get_raw_str(val)
    search_str = raw_str
    if isinstance(val, dict):
        search_str = raw_str + " " + str(val)

    results = []
    seen = set()
    for m in DOI_PATTERN.finditer(search_str):
        cleaned = clean_doi(m.group(0))
        if cleaned in seen:
            continue
        seen.add(cleaned)
        if isinstance(val, dict) and "url" in val:
            sole = is_sole_doi(str(val["url"]), cleaned)
        else:
            sole = is_sole_doi(raw_str, cleaned)
        results.append(("DOI", cleaned, raw_str, sole))
    for m in PMID_PATTERN.finditer(search_str):
        pmid_val = f"PMID:{m.group(1)}"
        if pmid_val in seen:
            continue
        seen.add(pmid_val)
        sole = is_sole_doi(raw_str, m.group(0))
        results.append(("PMID", pmid_val, raw_str, sole))
    return results


@click.command()
@click.option("--mongo-uri", required=True, help="MongoDB connection URI including database name, e.g. mongodb://localhost:27017/nmdc")
@click.option("--env-file", default=None, help="Path to .env file for MongoDB credentials (MONGO_USER, MONGO_PASSWORD)")
@click.option("--output-file", required=True, type=click.Path(), help="Output TSV file path")
@click.option("--verbose", is_flag=True, help="Show verbose/debug output")
def extract_nmdc_doi_inventory(mongo_uri, env_file, output_file, verbose):
    """Extract all DOI/PMID references from an NMDC MongoDB and write a TSV inventory."""
    client = get_mongo_client(mongo_uri=mongo_uri, env_file=env_file, debug=verbose)

    parsed = uri_parser.parse_uri(mongo_uri)
    db_name = parsed.get("database")
    if not db_name:
        raise click.UsageError("MongoDB URI must include a database name (e.g. mongodb://localhost:27017/nmdc)")
    db = client[db_name]

    rows = []

    # 1. study_set -> associated_dois (structured Doi objects)
    click.echo("Scanning study_set for associated_dois...", err=True)
    for doc in db.study_set.find({"associated_dois": {"$exists": True, "$ne": []}}):
        study_name = doc.get("name", "") or doc.get("title", "")
        for i, doi_obj in enumerate(doc.get("associated_dois", [])):
            rows.append({
                "collection": "study_set",
                "document_id": doc.get("id", ""),
                "path": f"associated_dois[{i}]",
                "ref_type": doi_obj.get("doi_category", ""),
                "doi_value": doi_obj.get("doi_value", ""),
                "doi_provider": doi_obj.get("doi_provider", ""),
                "doi_category": doi_obj.get("doi_category", ""),
                "doi_is_sole_value": "yes",
                "raw_context": f"study_name={study_name}",
            })
    click.echo(f"  Found {len(rows)} study DOIs", err=True)

    # 2. biosample_set -> known MIxS method fields for regex-extracted DOIs/PMIDs
    click.echo("Scanning biosample_set for DOI/PMID references...", err=True)
    biosample_count = 0
    for doc in db.biosample_set.find({}):
        bsm_name = doc.get("name", "") or doc.get("samp_name", "")
        bsm_id = doc.get("id", "")

        for field in BIOSAMPLE_FIELDS:
            val = doc.get(field)
            if val is None:
                continue

            for ref_type, ref_val, raw_str, sole in extract_refs_with_context(val):
                biosample_count += 1
                rows.append({
                    "collection": "biosample_set",
                    "document_id": bsm_id,
                    "path": field,
                    "ref_type": ref_type,
                    "doi_value": ref_val,
                    "doi_provider": "",
                    "doi_category": "",
                    "doi_is_sole_value": "yes" if sole else "no",
                    "raw_context": f"biosample_name={bsm_name}; raw_value={raw_str[:300]}",
                })
    click.echo(f"  Found {biosample_count} biosample references", err=True)

    # 3. Scan other *_set collections for any embedded DOIs
    for coll_name in OTHER_COLLECTIONS:
        coll = db[coll_name]
        count = coll.estimated_document_count()
        if count == 0:
            continue
        if verbose:
            click.echo(f"Scanning {coll_name} ({count} docs)...", err=True)
        other_count = 0
        for doc in coll.find({}):
            doc_id = doc.get("id", str(doc.get("_id", "")))
            doc_name = doc.get("name", "")

            for key, val in doc.items():
                if key == "_id":
                    continue
                for ref_type, ref_val, raw_str, sole in extract_refs_with_context(val):
                    other_count += 1
                    rows.append({
                        "collection": coll_name,
                        "document_id": doc_id,
                        "path": key,
                        "ref_type": ref_type,
                        "doi_value": ref_val,
                        "doi_provider": "",
                        "doi_category": "",
                        "doi_is_sole_value": "yes" if sole else "no",
                        "raw_context": f"name={doc_name}; raw_value={raw_str[:300]}",
                    })

        if other_count:
            click.echo(f"  Found {other_count} references in {coll_name}", err=True)

    # Write TSV output
    fieldnames = [
        "collection", "document_id", "path", "ref_type", "doi_value",
        "doi_provider", "doi_category", "doi_is_sole_value", "raw_context",
    ]
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    # Summary stats to stderr
    click.echo(f"\nTotal rows: {len(rows)}", err=True)
    click.echo(f"Written to: {output_file}", err=True)

    coll_counts = Counter(r["collection"] for r in rows)
    click.echo("\nBy collection:", err=True)
    for c, n in coll_counts.most_common():
        click.echo(f"  {c}: {n}", err=True)

    cat_counts = Counter(r["doi_category"] for r in rows if r["doi_category"])
    if cat_counts:
        click.echo("\nBy doi_category:", err=True)
        for c, n in cat_counts.most_common():
            click.echo(f"  {c}: {n}", err=True)

    ref_counts = Counter(r["ref_type"] for r in rows)
    click.echo("\nBy ref_type:", err=True)
    for c, n in ref_counts.most_common():
        click.echo(f"  {c}: {n}", err=True)

    sole_counts = Counter(r["doi_is_sole_value"] for r in rows)
    click.echo("\nBy doi_is_sole_value:", err=True)
    for c, n in sole_counts.most_common():
        click.echo(f"  {c}: {n}", err=True)

    unique_dois = set(r["doi_value"] for r in rows)
    click.echo(f"\nUnique DOI/reference values: {len(unique_dois)}", err=True)

    client.close()


if __name__ == "__main__":
    extract_nmdc_doi_inventory()
