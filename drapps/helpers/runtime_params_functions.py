import json
from pathlib import Path
from typing import Any, Dict, List

import click
import yaml


def read_metadata_yaml(metadata_file: Path) -> Dict[str, Any]:
    """
    Read and parse the contents of the metadata.yaml file.
    """
    try:
        with open(metadata_file, 'r') as file:
            metadata = yaml.safe_load(file)
        return metadata
    except FileNotFoundError:
        raise FileNotFoundError(f"metadata.yaml file not found at {metadata_file}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing metadata.yaml: {e}")


def str_to_numeric(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            click.echo(f"{value} is not a numeric value", err=True)


def verify_runtime_env_vars(metadata_file, runtime_env_vars) -> List[str]:
    """
    Verify that the runtime environment variables are valid.
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
                if param_type == "string":
                    valid_params.append(f'[{json.dumps(param)}]')
                elif param_type == "numeric":
                    param_value = param['value']
                    param['value'] = str_to_numeric(param_value)
                    valid_params.append(f'[{json.dumps(param)}]')
            else:
                print(
                    f"Invalid type for '{field_name}'. Expected '{valid_param_dict[field_name]}', got '{param_type}'."
                )
        else:
            print(f"Undefined parameter: '{field_name}'.")

    return valid_params
