#!/usr/bin/env python3

import click
import time
from pymongo import MongoClient
from quantulum3 import parser
from tqdm import tqdm

# Skip list developed by Claude and MAM on 2025-09-28/29 based on dimensional unit analysis
# Original criteria: Skip harmonized_names with <5% dimensional content rate from quantulum3 parsing
# Extended criteria: Skip fields containing name, id (whole word), type, method, regm, process, date
# Final criteria: MAM semantic review of data-driven skip candidates (2025-09-29)
# Additional expansion: 2025-10-12 - Issue #244 consistency improvements
# Categories skipped: identifiers, person_info, dates, categorical fields, descriptive text, methods, processes,
#                   administrative metadata, experimental protocols, qualitative classifications
# Semantic rules: ALWAYS skip *_regm, *_cond, *_meth, multi-part info about treatments/sources/names/locations
# Excludes 224 harmonized_names that are unlikely to contain extractable measurement data
SKIP_HARMONIZED_NAMES = {
    # Original collaborative skip list (156 fields)
    'agrochem_addition', 'al_sat_meth', 'ances_data', 'animal_diet', 'antibiotic_regm',
    'biospecimen_repository_sample_id', 'biomaterial_provider', 'biotic_regm', 'birth_control', 'birth_date',
    'biol_stat', 'breed', 'breeding_history', 'breeding_method', 'cell_line', 'climate_environment',
    'coll_site_geo_feat', 'collected_by', 'collection_date', 'collection_method', 'compound', 'crop_rotation',
    'cult_isol_date', 'cult_result', 'cult_result_org', 'cultivar', 'culture_collection', 'cur_vegetation',
    'cur_vegetation_meth', 'death_date', 'dermatology_disord', 'derived_from', 'diet', 'disease', 'drug_usage',
    'ecotype', 'encoded_traits', 'enrichment_protocol', 'env_broad_scale', 'env_local_scale', 'env_medium',
    'ethnicity', 'experimental_factor', 'extreme_event', 'facility_type', 'family_id', 'fao_class',
    'food_additive', 'food_origin', 'food_prod_char', 'food_product_qual', 'food_product_type', 'fungicide_regm',
    'gap_sample_id', 'gap_subject_id', 'gastrointest_disord', 'genetic_mod', 'genotype', 'geo_loc_name',
    'growth_facil', 'growth_hormone_regm', 'growth_med', 'health_state', 'herbicide_regm', 'host',
    'host_body_habitat', 'host_body_product', 'host_common_name', 'host_dependence', 'host_description',
    'host_disease', 'host_family_relationship', 'host_genotype', 'host_infra_specific_name', 'host_infra_specific_rank',
    'host_life_stage', 'host_name', 'host_number', 'host_occupation', 'host_phenotype', 'host_subject_id',
    'host_subspecf_genlin', 'host_taxid', 'host_tissue_sampled', 'ihmc_medication_code', 'investigation_type',
    'isolate', 'isolate_name_alias', 'isolation_source', 'lab_host', 'label', 'link_addit_analys', 'local_class_meth',
    'medic_hist_perform', 'metagenome_source', 'mineral_nutr_regm', 'neg_cont_type', 'non_mineral_nutr_regm',
    'nose_mouth_teeth_throat_disord', 'num_replicons', 'omics_observ_id', 'pesticide_regm', 'ph_meth',
    'ph_regm', 'plant_body_site', 'plant_product', 'plant_struc', 'pool_dna_extracts', 'pos_cont_type',
    'previous_land_use', 'previous_land_use_meth', 'primary_treatment', 'project_name', 'propagation',
    'purpose_of_sampling', 'race', 'radiation_regm', 'rainfall_regm', 'reactor_type', 'samp_capt_status',
    'samp_collect_device', 'samp_dis_stage', 'samp_mat_type', 'samp_source_mat_cat', 'samp_stor_device',
    'sample_name', 'sample_type', 'season', 'season_environment', 'sequenced_by', 'serotype', 'serovar',
    'sewage_type', 'sex', 'smoker', 'soil_texture_meth', 'soil_type', 'soil_type_meth', 'source_material_id',
    'specimen_voucher', 'strain', 'study_design', 'substrate', 'submitted_sample_id', 'submitted_subject_id',
    'sym_life_cycle_type', 'tissue', 'tot_n_meth', 'tot_nitro_cont_meth', 'tot_org_c_meth', 'train_line',
    'treatment', 'wastewater_type', 'water_content_soil_meth',

    # Additional MAM-reviewed skips from overnight analysis (52 fields)
    'analyte_type', 'basin_name', 'biospecimen_repository', 'body_habitat', 'build_occup_type', 'building_setting',
    'chem_administration', 'cur_land_use', 'diet_last_six_month', 'dominant_hand', 'drainage_class', 'env_package',
    'fertilizer_regm', 'field', 'filter_type', 'floor_struc', 'food_type_processed', 'forma', 'gap_accession',
    'gap_consent_code', 'gap_consent_short_name', 'gaseous_environment', 'growth_protocol', 'heat_cool_type',
    'host_cellular_loc', 'host_color', 'host_diet', 'host_sex', 'host_shape', 'host_symbiont', 'indoor_space',
    'indoor_surf', 'isol_growth_condt', 'last_clean', 'lat_lon', 'light_type', 'menarche', 'misc_param',
    'molecular_data_type', 'oxy_stat_samp', 'particle_class', 'perturbation', 'rel_to_oxygen', 'route_transmission',
    'samp_mat_process', 'sediment_type', 'serogroup', 'soil_horizon', 'soil_text_measure', 'special_diet',
    'submitter_handle', 'type_status',

    # Issue #244 additions (18 fields - 2025-10-12)
    # Regimen fields (*_regm) - consistency with existing regimen skips
    'watering_regm', 'air_temp_regm', 'humidity_regm', 'light_regm', 'salt_regm', 'water_temp_regm', 'standing_water_regm',

    # Condition fields (*_cond) - categorical/descriptive conditions
    'host_growth_cond', 'root_cond', 'store_cond',

    # Method fields (*_meth) - methodology descriptions, not measurements
    'salinity_meth', 'heavy_metals_meth', 'horizon_meth',

    # Multi-part descriptive fields - treatments, sources, names, locations
    'description', 'food_source', 'source_name', 'secondary_treatment', 'samp_store_loc'
}

@click.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/ncbi_metadata', help='MongoDB URI')
@click.option('--min-count', default=1, help='Minimum biosample count for content')
@click.option('--progress-every', default=25, help='Show quantulum3 input every N values')
@click.option('--batch-size', default=1000, help='Process in batches')
@click.option('--limit', default=None, type=int, help='Limit total processing for testing')
@click.option('--save-aggregation', is_flag=True, help='Save aggregation results to content_pairs_aggregated collection')
@click.option('--clear-output', is_flag=True, help='Clear output collection before processing')
def main(mongo_uri, min_count, progress_every, batch_size, limit, save_aggregation, clear_output):
    """Efficient measurement discovery using biosamples_attributes aggregation with skip list"""

    print(f"[{time.strftime('%H:%M:%S')}] Starting efficient measurement discovery...")
    print(f"[{time.strftime('%H:%M:%S')}] Using skip list: {len(SKIP_HARMONIZED_NAMES)} harmonized_names will be skipped")
    print(f"[{time.strftime('%H:%M:%S')}] Min biosample count filter: {min_count}")
    print(f"[{time.strftime('%H:%M:%S')}] Progress display every: {progress_every} values")
    if limit:
        print(f"[{time.strftime('%H:%M:%S')}] Limited to first: {limit} pairs (testing mode)")

    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client.get_default_database()

    # Aggregation to get (harmonized_name, content, count) with filtering
    print(f"[{time.strftime('%H:%M:%S')}] Running aggregation to get content counts...")

    # Pipeline for complete aggregation (includes ALL harmonized_names for content_pairs_aggregated)
    pipeline = [
        # Basic filters only - NO skip list here
        {"$match": {
            "harmonized_name": {"$exists": True, "$ne": None},
            "content": {"$exists": True, "$ne": None}
        }},
        # Group by harmonized_name + content
        {"$group": {
            "_id": {"harmonized_name": "$harmonized_name", "content": "$content"},
            "biosample_count": {"$sum": 1}
        }},
        # Filter by minimum biosample count
        {"$match": {"biosample_count": {"$gte": min_count}}},
        # Sort alphabetically by harmonized_name, then by content
        {"$sort": {"_id.harmonized_name": 1, "_id.content": 1}},
        # Add fields for easier access
        {"$project": {
            "harmonized_name": "$_id.harmonized_name",
            "content": "$_id.content",
            "biosample_count": 1,
            "_id": 0
        }}
    ]

    if limit:
        pipeline.append({"$limit": limit})

    start_time = time.time()
    cursor = db.biosamples_attributes.aggregate(pipeline, allowDiskUse=True)

    # Stream results to avoid loading all 64M documents into memory (Issue #262)
    agg_collection = db['content_pairs_aggregated'] if save_aggregation else None
    if save_aggregation:
        print(f"[{time.strftime('%H:%M:%S')}] Streaming aggregation results to content_pairs_aggregated collection...")
        agg_collection.drop()

    # Streaming variables
    agg_batch = []
    agg_batch_size = 10000
    quantulum_results = []
    total_count = 0
    saved_count = 0
    skipped_count = 0
    total_biosamples = 0
    first_five = []

    # Stream cursor and process in one pass
    for result in cursor:
        total_count += 1
        total_biosamples += result['biosample_count']

        # Collect first 5 for display
        if len(first_five) < 5:
            first_five.append(result)

        # Save to aggregation collection if requested
        if save_aggregation:
            result['aggregated_at'] = time.time()
            agg_batch.append(result)

            if len(agg_batch) >= agg_batch_size:
                agg_collection.insert_many(agg_batch)
                saved_count += len(agg_batch)
                agg_batch = []

                # Progress every 1M
                if saved_count % 1000000 == 0:
                    print(f"[{time.strftime('%H:%M:%S')}] Saved {saved_count:,} aggregation results...")

        # Filter for quantulum3 processing
        if result['harmonized_name'] not in SKIP_HARMONIZED_NAMES:
            quantulum_results.append(result)
        else:
            skipped_count += 1

    agg_time = time.time() - start_time

    # Save final aggregation batch
    if save_aggregation and agg_batch:
        agg_collection.insert_many(agg_batch)
        saved_count += len(agg_batch)
        print(f"[{time.strftime('%H:%M:%S')}] Saved {saved_count:,} aggregation results")

    print(f"[{time.strftime('%H:%M:%S')}] Aggregation completed in {agg_time:.1f}s")
    print(f"[{time.strftime('%H:%M:%S')}] Found {total_count:,} (harmonized_name, content) pairs with ≥{min_count} biosamples (ALL harmonized_names)")

    if total_count > 0:
        print(f"[{time.strftime('%H:%M:%S')}] Covering {total_biosamples:,} total biosample instances")
        print(f"[{time.strftime('%H:%M:%S')}] Top 5 most common:")
        for i, result in enumerate(first_five):
            print(f"[{time.strftime('%H:%M:%S')}]   {i+1}. {result['harmonized_name']}: \"{result['content']}\" ({result['biosample_count']:,} biosamples)")

    if total_count == 0:
        print(f"[{time.strftime('%H:%M:%S')}] No results found - try lowering min_count")
        return

    print(f"[{time.strftime('%H:%M:%S')}] Applying skip list for quantulum3 processing...")
    print(f"[{time.strftime('%H:%M:%S')}] Will process {len(quantulum_results):,} pairs ({skipped_count:,} pairs skipped)")

    # Process with quantulum3 in batches
    print(f"[{time.strftime('%H:%M:%S')}] Starting quantulum3 processing...")
    processed = 0
    parsed_results = []

    output_collection = db['measurement_results_skip_filtered']
    print(f"[{time.strftime('%H:%M:%S')}] Results will be stored in: measurement_results_skip_filtered")

    # Clear output collection if requested
    if clear_output:
        print(f"[{time.strftime('%H:%M:%S')}] Clearing existing results from measurement_results_skip_filtered...")
        output_collection.drop()
        print(f"[{time.strftime('%H:%M:%S')}] Output collection cleared")

    with tqdm(total=len(quantulum_results), desc="Processing with quantulum3") as pbar:
        for i, result in enumerate(quantulum_results):
            content = result['content']
            harmonized_name = result['harmonized_name']

            # Show progress every N items
            if i % progress_every == 0:
                print(f"\n[{time.strftime('%H:%M:%S')}] Progress {i+1}/{len(quantulum_results)}: Processing \"{content}\" for {harmonized_name}")

            # Skip content that doesn't contain both letter and digit (likely not measurement)
            has_letter = any(c.isalpha() for c in content)
            has_digit = any(c.isdigit() for c in content)

            if not (has_letter and has_digit):
                if i % progress_every == 0:
                    print(f"[{time.strftime('%H:%M:%S')}]   → Skipped: no letter+digit pattern")
                processed += 1
                pbar.update(1)
                continue

            try:
                parsed = parser.parse(str(content))
                if parsed:
                    for quantity in parsed:
                        # Calculate coverage percentage
                        coverage_pct = ((quantity.span[1] - quantity.span[0]) / len(content) * 100) if quantity.span and len(content) > 0 else 0

                        doc = {
                            'harmonized_name': harmonized_name,
                            'original_content': content,
                            'biosample_count': result['biosample_count'],
                            'value': quantity.value,
                            'unit': quantity.unit.name if quantity.unit else None,
                            'entity': quantity.unit.entity.name if quantity.unit and quantity.unit.entity else None,
                            'span_start': quantity.span[0] if quantity.span else None,
                            'span_end': quantity.span[1] if quantity.span else None,
                            'surface_text': quantity.surface if hasattr(quantity, 'surface') else None,
                            'coverage_pct': round(coverage_pct, 1),
                            'content_length': len(content),
                            'processed_at': time.time()
                        }
                        parsed_results.append(doc)

                        # Show detailed output for monitoring
                        if i % progress_every == 0:
                            print(f"[{time.strftime('%H:%M:%S')}]   → Parsed: {quantity.value} {quantity.unit.name if quantity.unit else 'dimensionless'}")

                else:
                    if i % progress_every == 0:
                        print(f"[{time.strftime('%H:%M:%S')}]   → No quantities detected")

            except Exception as e:
                if i % progress_every == 0:
                    print(f"[{time.strftime('%H:%M:%S')}]   → Parse error: {str(e)[:50]}")

            processed += 1
            pbar.update(1)

            # Save intermediate results every batch
            if processed % batch_size == 0 and parsed_results:
                print(f"\n[{time.strftime('%H:%M:%S')}] Saving batch: {len(parsed_results):,} results to MongoDB...")
                output_collection.insert_many(parsed_results)
                parsed_results = []  # Clear for next batch
                print(f"[{time.strftime('%H:%M:%S')}] Processed {processed:,}/{len(quantulum_results):,} so far")

    # Save final batch
    if parsed_results:
        print(f"\n[{time.strftime('%H:%M:%S')}] Saving final batch: {len(parsed_results):,} results...")
        output_collection.insert_many(parsed_results)

    total_saved = output_collection.count_documents({})
    print(f"\n[{time.strftime('%H:%M:%S')}] ✅ Processing complete!")
    print(f"[{time.strftime('%H:%M:%S')}] Total processed: {processed:,}")
    print(f"[{time.strftime('%H:%M:%S')}] Total quantities saved: {total_saved:,}")
    print(f"[{time.strftime('%H:%M:%S')}] Results collection: measurement_results_skip_filtered")

    if total_saved > 0:
        print(f"[{time.strftime('%H:%M:%S')}] Sample results from MongoDB:")
        samples = output_collection.find().limit(3)
        for result in samples:
            print(f"[{time.strftime('%H:%M:%S')}]   {result['harmonized_name']}: \"{result['original_content']}\" → {result['value']} {result['unit']} ({result['biosample_count']} biosamples)")

if __name__ == "__main__":
    main()