import pytest
import yaml
from click.testing import CliRunner
from external_metadata_awareness.env_local_scale_extraction import cli, load_configs, process_ontology


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
        "exclusions": [
            "biome",
            "environmental material",
            "chemical entity"
        ],
        "output": str(tmp_path / "output.txt")
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
    assert extraction_config["output"].endswith("output.txt")


def test_process_ontology(oak_config_file, extraction_config_file):
    _, extraction_config = load_configs(oak_config_file, extraction_config_file)

    # Replace with a real test ontology and expected behavior if possible.
    process_ontology(oak_config_file, extraction_config)

    # Check if the output file is created and has content
    assert extraction_config["output"]
    with open(extraction_config["output"], 'r') as file:
        content = file.read()
        print(content)
        assert len(content) > 0, "Output file is empty, expected some data."


def test_cli_runs_successfully(oak_config_file, extraction_config_file):
    runner = CliRunner()
    result = runner.invoke(cli, ['--extraction-config-file', str(extraction_config_file), '--oak-config-file',
                                 str(oak_config_file)])
    assert result.exit_code == 0
    assert "material entity" in result.output or "ENVO:00000447" in result.output  

    # Verify the output file exists and contains the expected results
    output_file = extraction_config_file.parent / "output.txt"
    assert output_file.exists()
    with open(output_file, 'r') as file:
        content = file.read()
        assert len(content) > 0, "Output file is empty, expected some data."