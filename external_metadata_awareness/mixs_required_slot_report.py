"""Report MIxS checklist/extension slots and their NMDC homes.

Iterates over the classes in a GSC MIxS schema, keeping only the checklist
classes (descendants of ``Checklist``) and the environmental extension classes
(descendants of ``Extension``). Combination classes (an extension with a
checklist mixed in, e.g. ``MigsBaSoil``) are deliberately excluded: the report
lists the checklists and extensions on their own so their slot requirements can
be read separately.

For every induced slot on each kept class the report records the slot's
``required`` and ``recommended`` status, whether the slot has an NMDC class home
and which NMDC classes carry it, and a relevance weight per environment.

Two weight sources are available (``--weight-source``):

- ``env-package`` (default): how many *realized* NMDC production biosamples
  carry each ``env_package``, read from the prod ``biosample_set`` over the
  jump-dev SSH tunnel (see docs/nmdc-prod-mongo-tunnel.md). Direct Mongo, no API.
- ``submission-rows``: how many *submitted* biosamples sit under each
  environment in the submission portal, from the flattened
  ``submission_biosample_rows`` collection. Captures in-progress submissions the
  realized data does not yet reflect.

Weights default to a baked-in snapshot so the report runs offline; pass
``--refresh-weights`` to recompute the chosen source live over MongoDB.

This extends the TSV-based crosswalk in ``mixs_slots_in_nmdc.py`` by adding
requirement status, checklist/extension/combination classification, per-class
homes, and environment weighting in a single SchemaView pass.

Example:
    mixs-required-slot-report -o local/mixs_required_slot_report.tsv
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote_plus

import click
from dotenv import dotenv_values
from linkml_runtime import SchemaView
from pymongo import MongoClient

# GSC MIxS v6.3.0 is the version NMDC imports slots from; see nmdc-schema's
# assets/import_mixs_slots_regardless.tsv.
DEFAULT_MIXS_SCHEMA = (
    "https://raw.githubusercontent.com/GenomicsStandardsConsortium/"
    "mixs/v6.3.0/src/mixs/schema/mixs.yaml"
)
# NMDC materialized schema, matching analyze_nmdc_biosample_coverage.py.
DEFAULT_NMDC_SCHEMA = (
    "https://raw.githubusercontent.com/microbiomedata/nmdc-schema/"
    "main/nmdc_schema/nmdc_materialized_patterns.yaml"
)

# Realized prod biosamples: the nmdc database reached over the jump-dev SSH
# tunnel on localhost:27124 (see docs/nmdc-prod-mongo-tunnel.md).
# directConnection=true is required (replica-set members advertise internal
# Kubernetes hostnames).
DEFAULT_PROD_MONGO_URI = (
    "mongodb://localhost:27124/nmdc?authSource=admin&directConnection=true"
)
# Submitted biosamples: EMA's flattened submission collection in local Mongo.
DEFAULT_SUBMISSION_MONGO_URI = "mongodb://localhost:27017/nmdc_metadata?authSource=admin"
DEFAULT_ENV_FILE = "local/.env"
DEFAULT_SUBMISSION_COLLECTION = "submission_biosample_rows"

# .env key pairs tried (in order) when a Mongo URI carries no inline credentials.
# Covers the cred-naming drift across repos: EMA uses MONGO_USER/PASSWORD;
# nmdc-schema's local/.env holds prod creds under SOURCE_MONGO_USER/SOURCE_MONGO_PASS.
MONGO_CRED_KEY_PAIRS = (
    ("MONGO_USER", "MONGO_PASSWORD"),
    ("SOURCE_MONGO_USER", "SOURCE_MONGO_PASS"),
    ("NMDC_MONGO_USER", "NMDC_MONGO_PASSWORD"),
)

# Root classes in the GSC MIxS class hierarchy.
CHECKLIST_ROOT = "Checklist"
EXTENSION_ROOT = "Extension"

# Normalize realized env_package raw values (lowercased) to MIxS extension
# classes. Values seen in prod are MIxS package labels plus a few ENVO CURIEs.
ENV_PACKAGE_TO_EXTENSION: dict[str, str] = {
    "soil": "Soil",
    "envo:00001998": "Soil",  # ENVO:00001998 is soil
    "water": "Water",
    "sediment": "Sediment",
    "air": "Air",
    "plant-associated": "PlantAssociated",
    "host-associated": "HostAssociated",
    "miscellaneous natural or artificial environment": "MiscellaneousNaturalOrArtificialEnvironment",
    "microbial mat/biofilm": "MicrobialMatBiofilm",
    "built environment": "BuiltEnvironment",
    "wastewater/sludge": "WastewaterSludge",
    "hydrocarbon resources-cores": "HydrocarbonResourcesCores",
}

# Map each submission-portal environment row key to its MIxS extension class.
ROW_KEY_TO_EXTENSION: dict[str, str] = {
    "soil_data": "Soil",
    "water_data": "Water",
    "sediment_data": "Sediment",
    "air_data": "Air",
    "plant_associated_data": "PlantAssociated",
    "host_associated_data": "HostAssociated",
    "misc_envs_data": "MiscellaneousNaturalOrArtificialEnvironment",
    "biofilm_data": "MicrobialMatBiofilm",
    "built_env_data": "BuiltEnvironment",
    "hcr_cores_data": "HydrocarbonResourcesCores",
    "wastewater_sludge_data": "WastewaterSludge",
}

# The full set of NMDC-supported extensions (an NMDC submission interface
# exists), so a source with zero biosamples in one still reports weight 0.
SUPPORTED_EXTENSIONS = sorted(set(ENV_PACKAGE_TO_EXTENSION.values()))

# Baked-in weight snapshots (biosample counts) per source, so the report runs
# offline. Refresh either live with --refresh-weights.
EXTENSION_WEIGHT_SNAPSHOTS: dict[str, dict[str, int]] = {
    # Realized NMDC production biosamples by env_package, from prod biosample_set
    # over the jump-dev tunnel (snapshot 2026-06-23; 12,380 of 16,663 biosamples
    # carry env_package). Realized prod currently holds no sediment/air/biofilm/
    # built-env/hydrocarbon/wastewater biosamples.
    "env-package": {
        "Soil": 10450,
        "Water": 1292,
        "MiscellaneousNaturalOrArtificialEnvironment": 293,
        "PlantAssociated": 284,
        "HostAssociated": 61,
        "Sediment": 0,
        "Air": 0,
        "MicrobialMatBiofilm": 0,
        "BuiltEnvironment": 0,
        "HydrocarbonResourcesCores": 0,
        "WastewaterSludge": 0,
    },
    # Submitted biosamples by environment, from submission_biosample_rows
    # (snapshot 2026-06-22; 25,065 environmental rows).
    "submission-rows": {
        "Soil": 17431,
        "Water": 3653,
        "Sediment": 1259,
        "Air": 808,
        "PlantAssociated": 746,
        "HostAssociated": 649,
        "MiscellaneousNaturalOrArtificialEnvironment": 440,
        "MicrobialMatBiofilm": 42,
        "BuiltEnvironment": 27,
        "HydrocarbonResourcesCores": 10,
        "WastewaterSludge": 0,
    },
}

# Checklists in scope: the environmental checklist (Mims) plus the
# bacteria/archaea checklist (MigsBa). This is the scope Alicia Clum set for the
# 2026-06-18 request.
NMDC_SUPPORTED_CHECKLISTS = frozenset({"Mims", "MigsBa"})

# Recency overlay: MIxS classes under active NMDC work that the weight snapshots
# do not yet reflect, so they should be upweighted. Keep reasons dated and
# issue-linked. Hand-curated, not derived from data.
NMDC_ACTIVE_WORK_BOOST: dict[str, str] = {
    # JGI isolate/organism modeling underway as of 2026-06; isolates export to
    # NCBI under the MIGS bacteria/archaea checklist. Tracking issue:
    # https://github.com/microbiomedata/nmdc-schema/issues/2803
    "MigsBa": "active 2026-06: JGI isolate modeling, exports to NCBI as MIGS-BA (#2803)",
}


def classify_mixs_class(schema_view: SchemaView, class_name: str) -> str:
    """Categorize a MIxS class as checklist, extension, combination, or other.

    Combination classes (e.g. ``MigsBaSoil``) are an extension with a checklist
    mixed in, so they are the only classes that carry mixins. Checklist and
    extension classes are identified by ancestry from the two MIxS roots.
    """
    class_definition = schema_view.get_class(class_name)
    if class_definition.mixins:
        return "combination"
    ancestors = set(schema_view.class_ancestors(class_name))
    if CHECKLIST_ROOT in ancestors:
        return "checklist"
    if EXTENSION_ROOT in ancestors:
        return "extension"
    return "other"


def is_nmdc_supported_class(
    class_name: str, class_type: str, extension_weights: dict[str, int]
) -> bool:
    """Whether a MIxS checklist/extension is in NMDC's supported scope.

    Extensions are "supported" if they have an NMDC submission interface (a key
    in extension_weights, including ones with zero biosamples in this source).
    """
    if class_type == "extension":
        return class_name in extension_weights
    if class_type == "checklist":
        return class_name in NMDC_SUPPORTED_CHECKLISTS
    return False


def nmdc_relevance_weight(
    class_name: str, class_type: str, extension_weights: dict[str, int]
) -> float | None:
    """Normalized NMDC relevance weight (0-1) for an extension class.

    Returns the extension's share of biosamples in the active weight source, or
    None for checklist classes (which are not usage-weighted here).
    """
    if class_type != "extension":
        return None
    total = sum(extension_weights.values()) or 1
    return extension_weights.get(class_name, 0) / total


def connect_mongo(mongo_uri: str, env_file: str | None) -> MongoClient:
    """Connect to MongoDB, injecting credentials from env_file when needed.

    If the URI has no inline credentials and env_file provides one of the
    MONGO_CRED_KEY_PAIRS, those are spliced into the URI. Credentials are never
    logged. The URI must include a database name.
    """
    final_uri = mongo_uri
    if "@" not in mongo_uri:
        config = {}
        if env_file and Path(env_file).exists():
            config = dotenv_values(env_file)
        elif env_file:
            click.echo(f"Warning: env file not found: {env_file}", err=True)
        for user_key, pass_key in MONGO_CRED_KEY_PAIRS:
            user, password = config.get(user_key), config.get(pass_key)
            if user and password:
                protocol, rest = mongo_uri.split("://", 1)
                final_uri = f"{protocol}://{quote_plus(user)}:{quote_plus(password)}@{rest}"
                break
        else:
            click.echo(
                "Warning: no credentials resolved (URI has none and the env "
                "file has none of these user/password pairs: "
                f"{', '.join(f'{u}/{p}' for u, p in MONGO_CRED_KEY_PAIRS)}); "
                "connecting unauthenticated, which will fail against an "
                "authenticated server.",
                err=True,
            )
    return MongoClient(final_uri, serverSelectionTimeoutMS=8000)


def fetch_env_package_weights(mongo_uri: str, env_file: str | None) -> dict[str, int]:
    """Count realized production biosamples per MIxS extension via env_package.

    Queries prod ``biosample_set`` over the jump-dev tunnel and normalizes each
    ``env_package.has_raw_value`` with ENV_PACKAGE_TO_EXTENSION.
    """
    client = connect_mongo(mongo_uri, env_file)
    collection = client.get_default_database()["biosample_set"]
    pipeline = [{"$group": {"_id": "$env_package.has_raw_value", "n": {"$sum": 1}}}]
    counts: dict[str, int] = {extension: 0 for extension in SUPPORTED_EXTENSIONS}
    for record in collection.aggregate(pipeline):
        raw = record["_id"]
        if not raw:
            continue
        extension = ENV_PACKAGE_TO_EXTENSION.get(str(raw).strip().lower())
        if extension:
            counts[extension] += record["n"]
    return counts


def fetch_submission_row_weights(
    mongo_uri: str, env_file: str | None, collection_name: str
) -> dict[str, int]:
    """Count submitted biosamples per MIxS extension from the submission rows.

    Groups the flattened submission collection by its environment row key (e.g.
    ``soil_data``) and maps each key to its MIxS extension.
    """
    client = connect_mongo(mongo_uri, env_file)
    collection = client.get_default_database()[collection_name]
    pipeline = [
        {"$match": {"key": {"$regex": "_data$"}}},
        {"$group": {"_id": "$key", "n": {"$sum": 1}}},
    ]
    counts = {record["_id"]: record["n"] for record in collection.aggregate(pipeline)}
    weights: dict[str, int] = {extension: 0 for extension in SUPPORTED_EXTENSIONS}
    for row_key, extension in ROW_KEY_TO_EXTENSION.items():
        weights[extension] = counts.get(row_key, 0)
    return weights


def load_annotations(annotations_path: Path) -> dict[str, tuple[str, str]]:
    """Load a curated per-slot annotations TSV into {slot: (priority, comment)}.

    The file must have a header row and the columns ``slot``, ``priority``,
    ``comment``. Annotations are keyed by slot name and applied to every row for
    that slot, since the coverage judgment is about the slot's concept.
    """
    annotations: dict[str, tuple[str, str]] = {}
    with annotations_path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for record in reader:
            slot_name = (record.get("slot") or "").strip()
            if not slot_name:
                continue
            annotations[slot_name] = (
                (record.get("priority") or "").strip(),
                (record.get("comment") or "").strip(),
            )
    return annotations


def build_nmdc_slot_homes(nmdc_schema_view: SchemaView) -> dict[str, list[str]]:
    """Map each slot name to the NMDC classes that induce it.

    A slot "has a home" in NMDC when it appears in the induced slots of at least
    one NMDC class.
    """
    slot_to_classes: dict[str, set[str]] = defaultdict(set)
    for class_name in nmdc_schema_view.all_classes():
        for slot_name in nmdc_schema_view.class_slots(class_name):
            slot_to_classes[slot_name].add(class_name)
    return {slot: sorted(classes) for slot, classes in slot_to_classes.items()}


def format_boolean(value: bool | None) -> str:
    """Render a LinkML boolean metaslot (True/None) as 'true'/'false'."""
    return "true" if value else "false"


@click.command()
@click.option(
    "--mixs-schema",
    default=DEFAULT_MIXS_SCHEMA,
    show_default=True,
    help="Path or URL to the GSC MIxS schema to read checklist/extension classes from.",
)
@click.option(
    "--schema-url",
    "-s",
    "nmdc_schema",
    default=DEFAULT_NMDC_SCHEMA,
    show_default=True,
    help="Path or URL to the NMDC schema used to find each slot's class home(s).",
)
@click.option(
    "--nmdc-home/--no-nmdc-home",
    default=True,
    show_default=True,
    help="Include columns reporting whether each MIxS slot has an NMDC class home.",
)
@click.option(
    "--weight-source",
    type=click.Choice(["env-package", "submission-rows"]),
    default="env-package",
    show_default=True,
    help="Weight by realized prod env_package (prod Mongo) or submitted rows (local Mongo).",
)
@click.option(
    "--refresh-weights",
    is_flag=True,
    default=False,
    help="Recompute the chosen weight source live over MongoDB instead of the baked snapshot.",
)
@click.option(
    "--prod-mongo-uri",
    default=DEFAULT_PROD_MONGO_URI,
    show_default=True,
    help="Prod Mongo URI (over the jump-dev tunnel) for the env-package source.",
)
@click.option(
    "--submission-mongo-uri",
    default=DEFAULT_SUBMISSION_MONGO_URI,
    show_default=True,
    help="Mongo URI for the submission-rows source.",
)
@click.option(
    "--env-file",
    default=DEFAULT_ENV_FILE,
    show_default=True,
    help="Path to a .env file supplying Mongo credentials when refreshing weights.",
)
@click.option(
    "--submission-collection",
    default=DEFAULT_SUBMISSION_COLLECTION,
    show_default=True,
    help="Flattened submission collection grouped by environment row key.",
)
@click.option(
    "--annotations",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Optional curated TSV (columns: slot, priority, comment) merged in as priority/comment.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    default=None,
    help="TSV output path. Writes to stdout when omitted.",
)
def main(
    mixs_schema: str,
    nmdc_schema: str,
    nmdc_home: bool,
    weight_source: str,
    refresh_weights: bool,
    prod_mongo_uri: str,
    submission_mongo_uri: str,
    env_file: str,
    submission_collection: str,
    annotations: Path | None,
    output: Path | None,
) -> None:
    """Write a TSV of MIxS checklist/extension slots and their NMDC homes."""
    if refresh_weights and weight_source == "env-package":
        click.echo("Refreshing env_package weights from prod biosample_set", err=True)
        extension_weights = fetch_env_package_weights(prod_mongo_uri, env_file)
    elif refresh_weights:
        click.echo("Refreshing submission-row weights from MongoDB", err=True)
        extension_weights = fetch_submission_row_weights(
            submission_mongo_uri, env_file, submission_collection
        )
    else:
        extension_weights = EXTENSION_WEIGHT_SNAPSHOTS[weight_source]
    click.echo(f"Weight source: {weight_source}", err=True)

    click.echo(f"Loading MIxS schema: {mixs_schema}", err=True)
    mixs_schema_view = SchemaView(mixs_schema)

    nmdc_slot_homes: dict[str, list[str]] = {}
    if nmdc_home:
        click.echo(f"Loading NMDC schema: {nmdc_schema}", err=True)
        nmdc_slot_homes = build_nmdc_slot_homes(SchemaView(nmdc_schema))

    slot_annotations: dict[str, tuple[str, str]] = {}
    if annotations:
        slot_annotations = load_annotations(annotations)
        click.echo(f"Merging {len(slot_annotations)} slot annotations", err=True)

    kept_classes = sorted(
        class_name
        for class_name in mixs_schema_view.all_classes()
        if classify_mixs_class(mixs_schema_view, class_name) in ("checklist", "extension")
    )
    click.echo(f"Reporting {len(kept_classes)} checklist/extension classes", err=True)

    header = [
        "mixs_class",
        "class_type",
        "nmdc_supported",
        "nmdc_relevance_weight",
        "nmdc_biosample_count",
        "nmdc_active_work",
        "nmdc_active_work_note",
        "slot",
        "required",
        "recommended",
    ]
    if nmdc_home:
        header += ["in_nmdc_schema", "nmdc_class_count", "nmdc_classes"]
    if slot_annotations:
        header += ["priority", "comment"]

    output_handle = output.open("w", newline="") if output else sys.stdout
    try:
        writer = csv.writer(output_handle, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        for class_name in kept_classes:
            class_type = classify_mixs_class(mixs_schema_view, class_name)
            supported = is_nmdc_supported_class(class_name, class_type, extension_weights)
            weight = nmdc_relevance_weight(class_name, class_type, extension_weights)
            biosample_count = extension_weights.get(class_name)
            active_work_note = NMDC_ACTIVE_WORK_BOOST.get(class_name, "")
            for slot_name in mixs_schema_view.class_slots(class_name):
                induced_slot = mixs_schema_view.induced_slot(slot_name, class_name)
                row = [
                    class_name,
                    class_type,
                    format_boolean(supported),
                    "" if weight is None else f"{weight:.4f}",
                    "" if biosample_count is None else str(biosample_count),
                    format_boolean(bool(active_work_note)),
                    active_work_note,
                    slot_name,
                    format_boolean(induced_slot.required),
                    format_boolean(induced_slot.recommended),
                ]
                if nmdc_home:
                    homes = nmdc_slot_homes.get(slot_name, [])
                    row += [
                        format_boolean(bool(homes)),
                        str(len(homes)),
                        "|".join(homes),
                    ]
                if slot_annotations:
                    priority, comment = slot_annotations.get(slot_name, ("", ""))
                    row += [priority, comment]
                writer.writerow(row)
    finally:
        if output:
            output_handle.close()

    if output:
        click.echo(f"Wrote {output}", err=True)


if __name__ == "__main__":
    main()
