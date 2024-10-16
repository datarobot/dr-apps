#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
from pathlib import Path
from typing import Optional

import click
from requests import Session

from .create import send_docker_image_with_progress
from .helpers.execution_environments_functions import create_execution_environment
from .helpers.wrappers import api_endpoint, api_token


@click.command()
@api_token
@api_endpoint
@click.option(
    '-n',
    '--name',
    required=True,
    type=click.STRING,
    help='Name of the execution env to be created',
)
@click.option(
    '-i',
    '--dockerfilezip',
    required=True,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    help='Path to tar archive which contains dockerfile',
)
@click.option(
    '-d',
    '--description',
    required=False,
    default=None,
    type=click.STRING,
    help='Description of the execution env to be created',
)
def create_env(
    token: str, endpoint: str, name: str, dockerfilezip: Path, description: Optional[str]
) -> None:
    """Creates an execution environment and a first version."""
    session = Session()
    session.headers.update({'Authorization': f'Bearer {token}'})
    click.echo('Creating execution environment')
    create_exec_env_rsp = create_execution_environment(
        session=session,
        endpoint=endpoint,
        env_name=name,
        description=description,
    )
    click.echo("Created Exec Environment")
    send_docker_image_with_progress(
        session=session,
        endpoint=endpoint,
        base_env_id=create_exec_env_rsp['id'],
        docker_image=dockerfilezip,
        field_name='docker_context',
    )
    click.echo()
