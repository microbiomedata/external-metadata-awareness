import pytest
import yaml
from click.testing import CliRunner
from external_metadata_awareness.env_local_scale_extraction import cli


@pytest.fixture
def sample_config(tmp_path):
    """
    :param tmp_path:
    :return:
    """

    # Create a sample config.yaml file for testing
    config_data = {
        "input": "sqlite:obo:envo",
        "output": "local/environmental-materials-relationships.txt",
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
    return str(config_file)


def test_generate_command(sample_config):
    """
    Test the generate_oak_command function.
    :param sample_config:
    :return:

    """
    runner = CliRunner()
    result = runner.invoke(cli, [sample_config])

    expected_command = (
        "$(RUN) runoak --input sqlite:obo:envo info [ .desc//p=i 'material entity' ]"
        " .not .desc//p=i 'biome'"
        " .not .desc//p=i 'environmental material'"
        " .not .desc//p=i 'chemical entity'"
        " > local/environmental-materials-relationships.txt"
    )

    assert result.exit_code == 0
    assert expected_command in result.output


def test_missing_config():
    """
    Test the CLI tool when the config file is missing.
    :return:

    """
    runner = CliRunner()
    result = runner.invoke(cli, ["nonexistent.yaml"])

    assert result.exit_code != 0
    assert "No such file or directory" in result.output


def test_invalid_config(tmp_path):
    """
    Test the CLI tool when the config file is invalid.
    :param tmp_path:
    :return:

    """
    invalid_config_file = tmp_path / "invalid_config.yaml"
    with open(invalid_config_file, 'w') as file:
        file.write("Invalid YAML content")

    runner = CliRunner()
    result = runner.invoke(cli, [str(invalid_config_file)])

    assert result.exit_code != 0
    assert "could not find expected" in result.output  # Checking for a YAML syntax error message
