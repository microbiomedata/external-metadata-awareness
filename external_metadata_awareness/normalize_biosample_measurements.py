import datetime
import sys
import time
from copy import deepcopy

import click
from pymongo import MongoClient
from quantulum3 import parser
from tqdm import tqdm

# these don't appear as a harmonized name attribute at all



###

# {
#   "Name": {
#     "content": "altitude"
#   },
#   "HarmonizedName": {
#     "content": "altitude"
#   },
#   "Synonym": {
#     "content": "alt"
#   },
#   "Description": {
#     "content": "The altitude of the sample is the vertical distance between Earth's surface above Sea Level and the sampled position in the air."
#   },
#   "Format": {
#     "content": "{float} m"
#   }
# }

curated_measurements = [
    "alt",
    "amount_light",
    "avg_dew_point",
    "carb_monoxide",
    "ceil_area",
    "ceil_thermal_mass",
    "diss_iron",
    "diss_oxygen_fluid",
    "association_duration",
    "crop_yield",
    "bacterial_density",
    "benzene",
    "blood_press_diast",
    "blood_press_syst",
    "cons_food_stor_temp",
    "cons_food_stor_dur",
    "built_struc_age",
    "api",
    "dew_point",
    "avg_temp",
    "biochem_oxygen_dem",
    "area_samp_size",
    "bac_resp",
    "barometric_press",
    "bac_prod",
    "chem_oxygen_dem",
    "down_par",
    "diss_inorg_nitro",
    "diss_inorg_phosp",
    "bishomohopanol",
    "aminopept_act",
    "alkyl_diethers",
    "bacteria_carb_prod",
    "diss_hydrogen",
    "diss_org_nitro",
    "bromide",
    "annual_precpt",
    "annual_temp",
    "al_sat",
    "diss_inorg_carb",
    "diss_carb_dioxide",
    "alkalinity",
    "abs_air_humidity",
    "calcium",
    "carb_dioxide",
    "chloride",
    "density",
    "diss_org_carb",
    "conduc",
    "air_temp",
    "chlorophyll",
    "ammonium",
    "diss_oxygen",
    "depth",
    "age",
    "altitude",  # (not a mixs term)
    "elev",
    "env_broad_scale",
    "geo_loc_name",
    "samp_size",
    "ph",
    "add_date", "address", "amount_light", "avg_dew_point", "avg_occup",
    "bathroom_count", "bedroom_count", "carb_monoxide", "carb_nitro_ratio",
    "ceil_area", "ceil_thermal_mass", "collection_time", "collection_time_inc",
    "community", "core field", "description", "dna_absorb1", "dna_absorb2",
    "dna_concentration", "dna_volume", "door_size", "ecosystem",
    "ecosystem_category", "ecosystem_subtype", "ecosystem_type",
    "efficiency_percent", "elevator", "env_package", "environment field",
    "escalator", "ethylbenzene", "exp_duct", "exp_pipe", "ext_door",
    "floor_age", "floor_area", "floor_count", "floor_thermal_mass", "fluor",
    "freq_cook", "glucosidase_act", "habitat", "hall_count", "hcr_fw_salinity",
    "hcr_pressure", "hcr_temp", "height_carper_fiber", "host_age",
    "host_body_temp", "host_dry_mass", "host_height", "host_length",
    "host_name", "host_tot_mass", "host_wet_mass", "humidity",
    "indust_eff_percent", "inside_lux", "investigation field",
    "isotope_exposure", "iwf", "lbc_thirty", "lbceq", "light_intensity",
    "location", "magnesium", "manganese", "max_occup", "mean_frict_vel",
    "mean_peak_frict_vel", "methane", "microbial_biomass",
    "microbial_biomass_c", "microbial_biomass_n", "mod_date", "name",
    "ncbi_taxonomy_name", "nitrate", "nitrate_nitrogen", "nitrite",
    "nitrite_nitrogen", "nitro", "nucleic acid sequence source field",
    "number_pets", "number_plants", "number_resident", "occup_density_samp",
    "occup_samp", "org_carb", "org_matter", "org_nitro", "owc_tvdss", "oxygen",
    "part_org_carb", "part_org_nitro", "permeability", "petroleum_hydrocarb",
    "phosphate", "photon_flux", "porosity", "potassium", "pour_point",
    "pressure", "primary_prod", "prod_rate", "proport_woa_temperature",
    "redox_potential", "rel_air_humidity", "rel_humidity_out",
    "replicate_number", "rna_absorb1", "rna_absorb2", "rna_concentration",
    "rna_volume", "room_air_exch_rate", "room_count", "room_dim",
    "room_door_dist", "room_moist_dam_hist", "room_net_area", "room_occup",
    "room_vol", "room_window_count", "root_med_ph", "salinity",
    "salinity_category", "samp_loc_corr_rate", "samp_room_id",
    "samp_store_dur", "samp_store_temp", "samp_time_out", "samp_tvdss",
    "sample_collection_site", "sample_shipped", "season_precpt",
    "season_temp", "sequencing field", "silicate", "size_frac",
    "size_frac_low", "size_frac_up", "slope_aspect", "slope_gradient",
    "sludge_retent_time", "sodium", "soil_text_measure", "solar_irradiance",
    "soluble_iron_micromol", "soluble_react_phosp", "specific_ecosystem",
    "specific_humidity", "start_time_inc", "subsurface_depth", "sulfate",
    "sulfate_fw", "sulfide", "surf_humidity", "surf_moisture",
    "surf_moisture_ph", "surf_temp", "suspend_part_matter", "tan",
    "technical_reps", "temp", "temp_out", "toluene", "tot_carb",
    "tot_depth_water_col", "tot_diss_nitro", "tot_inorg_nitro", "tot_iron",
    "tot_nitro", "tot_nitro_content", "tot_org_carb", "tot_part_carb",
    "tot_phosp", "tot_phosphate", "tot_sulfur", "turbidity",
    "tvdss_of_hcr_press", "tvdss_of_hcr_temp", "typ_occup_density",
    "ventilation_rate", "vfa", "vfa_fw", "viscosity", "wall_area",
    "wall_height", "wall_thermal_mass", "water_current", "water_cut",
    "water_feat_size", "water_prod_rate", "wind_speed", "window_open_freq",
    "window_size", "xylene", "zinc"
]


def ensure_index(collection, field_name):
    """Ensure an ascending index exists on the given field."""
    existing_indexes = collection.index_information()
    if field_name not in [list(i["key"])[0][0] for i in existing_indexes.values()]:
        collection.create_index([(field_name, 1)])
        click.echo(f"[{timestamp()}] Created index on '{collection.name}.{field_name}'")
    else:
        click.echo(f"[{timestamp()}] Index already exists on '{collection.name}.{field_name}'")


def clean_dict(d):
    """Recursively remove empty lists/dicts from a dictionary."""
    if isinstance(d, list):
        return [clean_dict(x) for x in d if clean_dict(x) not in ({}, [], None)]
    elif isinstance(d, dict):
        return {k: clean_dict(v) for k, v in d.items() if clean_dict(v) not in ({}, [], None)}
    else:
        return d


def timestamp():
    """Return ISO 8601 formatted timestamp."""
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def format_quantity_value(q):
    """Format the quantity value with uncertainty if present."""
    unit_name = q['unit']['name'] if q['unit']['name'] != "dimensionless" else ""

    if 'uncertainty' in q and q['uncertainty'] is not None:
        lower = q['value'] - q['uncertainty']
        upper = q['value'] + q['uncertainty']
        return f"{lower}-{upper} {unit_name}".strip()
    else:
        return f"{q['value']} {unit_name}".strip()


def aggregate_measurements(client, db_name, input_collection, output_collection, field_name, extra_verbose, overwrite):
    """Aggregate measurements from the specified field."""
    db = client[db_name]

    click.echo(
        f"[{timestamp()}] Step 1: Aggregating unique values for field '{field_name}' from collection '{input_collection}'...")

    # Check if input collection exists
    if input_collection not in db.list_collection_names():
        click.echo(
            f"[{timestamp()}] Error: Input collection '{input_collection}' does not exist in database '{db_name}'",
            err=True)
        sys.exit(1)

    # Create the aggregation pipeline
    pipeline = [
        {"$match": {field_name: {"$exists": True, "$ne": None}}},
        {"$group": {"_id": f"${field_name}", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]

    # Get count of matching documents for progress reporting
    match_count = db[input_collection].count_documents({field_name: {"$exists": True, "$ne": None}})
    click.echo(
        f"[{timestamp()}] Found {match_count} documents with field '{field_name}' in collection '{input_collection}'")

    # Run the aggregation
    click.echo(f"[{timestamp()}] Running aggregation pipeline...")
    start_time = time.time()
    result = list(db[input_collection].aggregate(pipeline))
    end_time = time.time()
    click.echo(f"[{timestamp()}] Aggregation completed in {end_time - start_time:.2f} seconds")
    click.echo(f"[{timestamp()}] Identified {len(result)} unique values for field '{field_name}'")

    # Create output collection if it doesn't exist
    if output_collection not in db.list_collection_names():
        click.echo(f"[{timestamp()}] Creating new collection '{output_collection}'...")
    else:
        # Check for existing documents with the same harmonized name
        existing_count = db[output_collection].count_documents({"harmonized_name": field_name})
        if existing_count > 0:
            if overwrite:
                click.echo(
                    f"[{timestamp()}] Removing {existing_count} existing documents for field '{field_name}' from '{output_collection}'...")
                db[output_collection].delete_many({"harmonized_name": field_name})
            else:
                click.echo(
                    f"[{timestamp()}] Warning: {existing_count} documents for field '{field_name}' already exist in '{output_collection}'")
                click.echo(
                    f"[{timestamp()}] Skipping aggregation for field '{field_name}'. Use --overwrite to replace existing data.")
                return None

    # Insert documents with the harmonized_name field
    click.echo(
        f"[{timestamp()}] Adding {len(result)} documents for field '{field_name}' to collection '{output_collection}'...")
    with tqdm(total=len(result), desc=f"[{timestamp()}] Inserting documents", unit="doc") as pbar:
        for doc in result:
            db[output_collection].insert_one({
                "_id": f"{field_name}:{doc['_id']}",  # Namespace the ID to avoid collisions
                "original_value": doc["_id"],
                "harmonized_name": field_name,
                "count": doc["count"]
            })
            pbar.update(1)

    click.echo(
        f"[{timestamp()}] Successfully added {len(result)} documents for field '{field_name}' to collection '{output_collection}'")
    return field_name


def parse_measurements(client, db_name, collection_name, field_name, extra_verbose):
    """Parse measurements using quantulum3."""
    db = client[db_name]
    col = db[collection_name]

    click.echo(
        f"[{timestamp()}] Step 2: Parsing measurement values for field '{field_name}' in collection '{collection_name}'...")

    # Get total document count for progress reporting
    total_docs = col.count_documents({"harmonized_name": field_name})
    click.echo(f"[{timestamp()}] Found {total_docs} documents to process for field '{field_name}'")

    parsed_count = 0
    skipped_count = 0

    # Iterate over documents with progress bar
    with tqdm(total=total_docs, desc=f"[{timestamp()}] Parsing measurements", unit="doc") as pbar:
        for doc in col.find({"harmonized_name": field_name}):
            raw_val = doc["original_value"]

            try:
                parsed = parser.parse(str(raw_val))  # Ensure it's a string
            except Exception as e:
                if extra_verbose:
                    click.echo(f"[{timestamp()}] Error parsing '{raw_val}': {str(e)}")
                skipped_count += 1
                pbar.update(1)
                continue

            if not parsed:
                if extra_verbose:
                    click.echo(f"[{timestamp()}] No quantity detected in '{raw_val}'")
                skipped_count += 1
                pbar.update(1)
                continue

            # Convert Quantity objects to JSON-serializable dicts
            parsed_dicts = []
            for q in parsed:
                try:
                    # Create a copy of the object's dict
                    q_dict = deepcopy(q.__dict__)

                    # Convert unit object to a simple dictionary
                    if 'unit' in q_dict and hasattr(q_dict['unit'], 'name'):
                        q_dict['unit'] = {
                            'name': q_dict['unit'].name,
                            'entity': q_dict['unit'].entity.name if hasattr(q_dict['unit'].entity, 'name') else str(
                                q_dict['unit'].entity),
                            'uri': str(q_dict['unit'].uri) if hasattr(q_dict['unit'], 'uri') else None
                        }

                    # Convert span tuple to list for better MongoDB compatibility
                    if 'span' in q_dict and isinstance(q_dict['span'], tuple):
                        q_dict['span'] = list(q_dict['span'])

                    # Clean the dictionary
                    cleaned_dict = clean_dict(q_dict)
                    parsed_dicts.append(cleaned_dict)
                except Exception as e:
                    if extra_verbose:
                        click.echo(f"[{timestamp()}] Error processing parsed result for '{raw_val}': {str(e)}")

            # Remove any completely empty results
            parsed_dicts = [pd for pd in parsed_dicts if pd]

            if parsed_dicts:
                reconstructed_values = []
                try:
                    # Generate reconstructed values
                    reconstructed_values = [format_quantity_value(q) for q in parsed_dicts]

                    # Update the document with parsed quantities
                    col.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {
                            "parsed_quantity": parsed_dicts,
                            "reconstructed": reconstructed_values
                        }}
                    )
                    parsed_count += 1

                    if extra_verbose:
                        click.echo(
                            f"[{timestamp()}] Successfully parsed '{raw_val}' → {', '.join(reconstructed_values)}")
                except Exception as e:
                    if extra_verbose:
                        click.echo(f"[{timestamp()}] Error updating document for '{raw_val}': {str(e)}")
                    skipped_count += 1
            else:
                skipped_count += 1
                if extra_verbose:
                    click.echo(f"[{timestamp()}] No valid parsed results for '{raw_val}'")

            pbar.update(1)

    # Summary statistics
    if total_docs > 0:
        click.echo(f"[{timestamp()}] Parsing summary for field '{field_name}':")
        click.echo(f"[{timestamp()}]   - Total documents: {total_docs}")
        click.echo(
            f"[{timestamp()}]   - Successfully parsed: {parsed_count} ({(parsed_count / total_docs) * 100:.2f}%)")
        click.echo(f"[{timestamp()}]   - Skipped/failed: {skipped_count} ({(skipped_count / total_docs) * 100:.2f}%)")
    else:
        click.echo(f"[{timestamp()}] No documents processed for field '{field_name}'")

    return parsed_count


@click.command()
@click.option('--mongodb-uri', default='mongodb://localhost:27017', help='MongoDB connection URI')
@click.option('--db-name', default='ncbi_metadata', help='Database name')
@click.option('--input-collection', default='biosamples_flattened', help='Input collection name')
@click.option('--output-collection', default='biosamples_measurements', help='Output collection name')
@click.option('--field', required=False, multiple=True, default=curated_measurements, help='Field name(s) to parse.')
@click.option('-v', '--verbosity', type=click.Choice(['quiet', 'normal', 'verbose']), default='normal',
              help='Verbosity level')
@click.option('--overwrite', is_flag=True, help='Overwrite existing data for the specified field(s)')
def main(mongodb_uri, db_name, input_collection, output_collection, field, verbosity, overwrite):
    try:
        is_quiet = verbosity == 'quiet'
        is_verbose = verbosity == 'verbose'

        if not is_quiet:
            click.echo(f"[{timestamp()}] Connecting to MongoDB at {mongodb_uri}...")
        client = MongoClient(mongodb_uri)
        client.admin.command('ping')

        db = client[db_name]
        input_col = db[input_collection]
        output_col = db[output_collection]

        total_start_time = time.time()
        fields_processed = 0
        total_parsed = 0

        for current_field in field:
            click.echo(f"[{timestamp()}] Ensuring index on '{current_field}' in '{input_collection}'...")
            ensure_index(input_col, current_field)

            if not is_quiet:
                click.echo(f"[{timestamp()}] ------------------------------------------------------------")
                click.echo(f"[{timestamp()}] Processing field: '{current_field}'")

            field_start_time = time.time()

            # Step 1: Aggregate
            processed_field = aggregate_measurements(
                client, db_name, input_collection, output_collection,
                current_field, is_verbose, overwrite
            )

            if processed_field is None:
                click.echo(f"[{timestamp()}] Skipping field '{current_field}' (likely due to overwrite=False)")
                continue

            ensure_index(output_col, "harmonized_name")

            # Step 2: Parse
            parsed_count = parse_measurements(
                client, db_name, output_collection, current_field, is_verbose
            )

            # Drop index on input field
            click.echo(f"[{timestamp()}] Dropping index on '{current_field}' from '{input_collection}'...")
            try:
                input_col.drop_index(f"{current_field}_1")
                click.echo(f"[{timestamp()}] Index '{current_field}_1' dropped successfully.")
            except Exception as e:
                click.echo(f"[{timestamp()}] Warning: Failed to drop index '{current_field}_1': {str(e)}")

            # Summary per field
            field_end_time = time.time()
            click.echo(
                f"[{timestamp()}] Field '{current_field}' processed in {field_end_time - field_start_time:.2f} seconds")

            fields_processed += 1
            total_parsed += parsed_count

        total_end_time = time.time()
        if not is_quiet:
            click.echo(f"[{timestamp()}] ============================================================")
            click.echo(f"[{timestamp()}] Fields processed: {fields_processed} of {len(field)}")
            click.echo(f"[{timestamp()}] Total parsed documents: {total_parsed}")
            click.echo(f"[{timestamp()}] Total processing time: {total_end_time - total_start_time:.2f} seconds")
            click.echo(f"[{timestamp()}] Operation complete.")

    except Exception as e:
        click.echo(f"[{timestamp()}] ERROR: {str(e)}")
        raise


if __name__ == "__main__":
    main()
