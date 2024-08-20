from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import click
import yaml


def read_metadata_yaml(metadata_file: Tuple[Path, str]) -> Dict[str, Any]:
    """
    Read and parse the contents of the metadata.yaml file.

    Args:
    metadata_file (Tuple[Path, str]): A tuple containing the absolute and relative paths of metadata.yaml.

    Returns:
    Dict[str, Any]: A dictionary containing the parsed contents of the metadata.yaml file.

    Raises:
    FileNotFoundError: If the metadata file doesn't exist.
    yaml.YAMLError: If there's an error parsing the YAML file.
    """
    absolute_path, _ = metadata_file
    try:
        with open(absolute_path, 'r') as file:
            metadata = yaml.safe_load(file)
        return metadata
    except FileNotFoundError:
        raise FileNotFoundError(f"metadata.yaml file not found at {absolute_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing metadata.yaml: {e}")


def verify_runtime_env_vars(
    metadata_file: Tuple[Path, str], runtime_env_vars: List[Dict]
) -> Dict[str, Union[str, int]]:
    """
    Verify that the runtime environment variables are valid and return the valid ones.

    Args:
    metadata_file: The metadata file tuple (as returned by extract_metadata_yaml).
    runtime_env_vars: The runtime environment variables (as returned by get_runtime_params).

    Returns:
    Dict[str, Union[str, int]]: A dictionary of valid runtime parameters.
    """
    metadata_contents = read_metadata_yaml(metadata_file)
    valid_params: Dict[str, Union[str, int]] = {}

    # Create a dictionary of valid parameters from metadata for easy lookup
    valid_param_dict = {
        param['fieldName']: param['type']
        for param in metadata_contents.get('runtimeParameterDefinitions', [])
    }

    for param in runtime_env_vars:
        field_name = param['fieldName']
        param_value = param['value']
        param_type = param['type']

        if field_name in valid_param_dict and valid_param_dict[field_name] == param_type:
            if param_type == 'integer':
                try:
                    valid_params[field_name] = int(param_value)
                except ValueError:
                    click.echo(
                        f"Error: Invalid value for '{field_name}'. Expected integer, got '{param_value}'.",
                        err=True,
                    )
            elif param_type == 'string':
                valid_params[field_name] = param_value
            else:
                click.echo(
                    f"Error: Invalid datatype for '{field_name}'. Can be either string or integer.",
                    err=True,
                )
        else:
            click.echo(f"Error: Invalid parameter: '{field_name}'.", err=True)

    return valid_params
