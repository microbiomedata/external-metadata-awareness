# ms_material_processing_curation
This repo is a place for the MS Material Processing Metadata Squad to save scripts and files related to the curation of the mass spectrometry material processing and processed sample metadata.

## step1_pull_ms_samps
This folder includes two scripts:
1. materialprocessing_metadata.py:
   - Written by Sam O. This script pulls all mass spectrometry data generation objects from Mongo DB and their corresponding study and biosample information. It outputs several excel files (also in this folder) by study. Each excel file has a tab for each `analyte_category` (e.g. `metaproteome`, `metabolome`, and `nom`.)
2. pull_mass_spec_samps.py
   - Written by Brynn. This was a cursory initial script to pull all data generation objects and group by biosample `id` to explore the data intiially. 

## templates_and_examples
This folder includes:
1. A yaml template of all the relevant material processing classes in the NMDC Schema. Note that it does not include `LibraryPreparation` and it includes `StorageProcess` and `ProtocolExecution`. 
2. An example yaml file of a protocol outline that is two steps: a `Subsampling` process and a `ChromatographicSeparationProcess`

## metadata_gen_scripts
This folder includes:
1. `changesheet_gen.py` file that has the `ChangeSheetGenerator` class used to create changesheets.
2. `data_parser.py` file. This includes the `DataParser` class which is being used as a generic class to do any data parsing on any files before they run through the metadata generation processes. Such as getting the metadata into a dataframe from the Excel files by study and sheet name. Adding QuanittyValues to the yaml data using additional files for values.
3. `material_processing_metadata_gen.py` file includes the `MaterialProcessingMetadastaGenerator` class that generates the NMDC material processing metadata including minting ids, and creating a json dump file. This script should stay as general and reusable as possible, so it can be used in other uses cases (besides just retrospective material processing curation).

## studies
This folder contains the following files by study name / analyte_category:
1. The general yaml outlines created by Bea and Montana
2. Any additional info (such as `additional_info.tsv`) created by Montana and Bea's curation that include sample-specific metadata that differs across samples and so cannot be contained in the generic yaml file. Though the yaml file should have notes that refer to additional info.
3. A `main.py` file that generates the nmdc json dump file (to be submitted through the NMDC API) and changesheet that updates the `has_input` slot value of the `DataGeneration` records with the last processed sample output in the material processing steps (Also to be submitted through the NMDC API)
4. The `output.json` file that is an output of the `main.py` file. This includes all the NMDC metadata that has been created for Material Processing and the associated samples and will need to be submitted using the json submit endpoint.
5. The `changesheet.csv` that is an output of the `main.py` file. This includes the updated `has_input` slot values with the newly create processed samples that ended the material processing steps. To be submitted via the changesheets endpoint.

