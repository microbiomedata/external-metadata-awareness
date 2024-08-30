import pytest
import yaml
import os
from click.testing import CliRunner
from external_metadata_awareness.envo_local_scale_extraction import cli, load_configs, extract_terms_to_file
from oaklib.query import onto_query
from oaklib.selector import get_adapter


@pytest.fixture
def oak_config_file(tmp_path):
    config_data = {
        "ontology_resources": {
            "envo": {
                "selector": "sqlite:obo:envo"
            }
        }
    }
    config_file = tmp_path / "oak_config.yaml"
    with open(config_file, 'w') as file:
        yaml.dump(config_data, file)
    return config_file


@pytest.fixture
def extraction_config_file(tmp_path):
    config_data = {
        "entity": "material entity",
        "term_exclusions": [
            "bridge",
            "road",
            "wildlife management area"
        ],
        "term_and_descendant_exclusions": [
            "biome"
            , "environmental material"
            , "chemical entity"
            , "organic material"
            , "anatomical entity"
            , "organism"
            , "plant anatomical entity"
            , "healthcare facility"
            , "fluid layer"
            , "interface layer"
            , "manufactured product"
            , "anatomical entity environment"
            , "ecosystem"
            , "area protected according to IUCN guidelines"
            , "astronomical body"
            , "astronomical object"
            , "cloud"
            , "collection of organisms"
            , "environmental system"
            , "ecozone"
            , "material isosurface"
            , "environmental zone"
            , "water current"
            , "mass of environmental material"
            , "subatomic particle"
            , "observing system"
            , "particle"
            , "planetary structural layer"
            , "political entity"
            , "meteor"
            , "room"
            , "transport feature"
            , "mass of liquid"
            , "RO:0001025 water body"
            , "BFO:0000050 environmental monitoring area"
            , "BFO:0000050 marine littoral zone"
            , "BFO:0000050 marine environmental zone"
            , "RO:0002473 sea floor"
            , "BFO:0000050 saline water"
            , "BFO:0000050 ice"
            , "RO:0001025 water body"
            , "administrative region"
            , "protected area"
            , "channel of a watercourse"
            , "cryospheric layer"
            , "material isosurface"
            , "NCBITaxon:1"
            , "aeroform"
        ],
        "text_exclusions": [
            "gaseous"
            , "marine"
            , "undersea"
            , "saline"
            , "brackish"
        ],
        "output": str(tmp_path / "environmental-materials-relationships.txt")
    }
    config_file = tmp_path / "extraction_config.yaml"
    with open(config_file, 'w') as file:
        yaml.dump(config_data, file)
    return config_file


def test_load_configs(oak_config_file, extraction_config_file):
    oak_config, extraction_config = load_configs(oak_config_file, extraction_config_file)
    assert "ontology_resources" in oak_config
    assert "envo" in oak_config["ontology_resources"]
    assert oak_config["ontology_resources"]["envo"]["selector"] == "sqlite:obo:envo"
    assert extraction_config["entity"] == "material entity"
    assert "term_exclusions" in extraction_config
    assert "text_exclusions" in extraction_config
    assert extraction_config["output"].endswith("output.txt")


def test_process_ontology(oak_config_file, extraction_config_file):
    _, extraction_config = load_configs(oak_config_file, extraction_config_file)

    # Run the ontology processing
    extract_terms_to_file(oak_config_file, extraction_config)

    # Check if the output file is created and has content
    output_file_path = extraction_config["output"]
    assert os.path.exists(output_file_path), "Output file was not created"

    with open(output_file_path, 'r') as file:
        content = file.read()
        assert len(content) > 0, "Output file is empty, expected some data."

    # You could also add assertions based on expected content
    # For example, checking that excluded terms are not in the output
    assert "biome" not in content
    assert "brackish" not in content
    assert "saline" not in content


def test_cli_runs_successfully(oak_config_file, extraction_config_file):
    runner = CliRunner()
    result = runner.invoke(cli, ['--extraction-config-file', str(extraction_config_file), '--oak-config-file',
                                 str(oak_config_file)])
    assert result.exit_code == 0

    # Verify the output file exists and contains the expected results
    output_file = extraction_config_file.parent / "environmental-materials-relationships.txt"
    assert output_file.exists()
    with open(output_file, 'r') as file:
        content = file.read()
        assert len(content) > 0, "Output file is empty, expected some data."

    # Add additional assertions to check that the CLI correctly excluded terms
    assert "biome" not in content
    assert "brackish" not in content
    assert "saline" not in content


def test_onto_query():
    adapter = get_adapter("sqlite:obo:envo")
    # desc = onto_query([".desc//p=i", "material entity"], adapter)
    # print(len(desc))

    list_to_exclude = onto_query(["l~saline"], adapter, labels=True)
    print(list_to_exclude)