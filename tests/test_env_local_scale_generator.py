import pytest
import os
import yaml
from click.testing import CliRunner
from external_metadata_awareness.env_local_scale_extraction import cli, load_config, process_ontology


@pytest.fixture
def config_file(tmp_path):
    config_data = {
        "input": "sqlite:obo:envo",
        "output": str(tmp_path / "output.txt"),
        "entity": "material entity",
        "exclusions": [
            "biome",
            "environmental material",
            "chemical entity"
        ]
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as file:
        yaml.dump(config_data, file)
    return config_file


def test_load_config(config_file):
    config = load_config(config_file)
    assert config['input'] == "sqlite:obo:envo"
    assert config['output'].endswith("output.txt")
    assert config['entity'] == "material entity"
    assert "biome" in config['exclusions']


def test_process_ontology(config_file):
    config = load_config(config_file)
    process_ontology(config)

    # Check if the output file is created and not empty
    assert os.path.exists(config['output'])
    with open(config['output'], 'r') as file:
        content = file.read()
        assert len(content) > 0, "Output file is empty, expected some data."


def test_cli_runs_successfully(config_file):
    runner = CliRunner()
    result = runner.invoke(cli, ['--config-file', str(config_file)])
    assert result.exit_code == 0
    assert os.path.exists(load_config(config_file)['output'])


def test_no_exclusions(config_file):
    config = load_config(config_file)
    config['exclusions'] = []
    process_ontology(config)

    # Check if the output file is created and has content
    assert os.path.exists(config['output'])
    with open(config['output'], 'r') as file:
        content = file.read()
        assert len(content) > 0, "Output file is empty, expected some data even without exclusions."
