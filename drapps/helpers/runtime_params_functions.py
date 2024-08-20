from importlib.metadata import metadata
from pathlib import Path
from typing import Any, Dict, Tuple

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


def verify_runtime_env_vars(metadata_file, runtime_env_vars):
    """
    Verify that the runtime environment variables are valid.

    Args:
    metadata_file: The metadata file tuple (as returned by extract_metadata_yaml).
    runtime_env_vars: The runtime environment variables (as returned by get_runtime_params).

    Returns:
    Tuple[List[Dict], List[str]]: A tuple containing a list of valid runtime parameters
    and a list of error messages for invalid parameters.
    """
    metadata_contents = read_metadata_yaml(metadata_file)
    valid_params = []

    # Create a dictionary of valid parameters from metadata for easy lookup
    valid_param_dict = {
        param['fieldName']: param['type']
        for param in metadata_contents.get('runtimeParameterDefinitions', [])
    }

    for param in runtime_env_vars:
        field_name = param['fieldName']
        param_type = param['type']

        if field_name in valid_param_dict:
            if valid_param_dict[field_name] == param_type:
                valid_params.append(param)
            else:
                print(
                    f"Invalid type for '{field_name}'. Expected '{valid_param_dict[field_name]}', got '{param_type}'."
                )
        else:
            print(f"Undefined parameter: '{field_name}'.")

    return valid_params
