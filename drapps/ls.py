#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
from typing import Any, Dict, List

import click
from requests import Session
from tabulate import tabulate

from .helpers.custom_apps_functions import get_custom_apps_list
from .helpers.execution_environments_functions import get_execution_environments_list
from .helpers.wrappers import api_endpoint, api_token


def format_table(data: List[Dict[str, Any]], headers: List[str]) -> str:
    rows = []
    for element in data:
        rows.append([element[column] for column in headers])
    return tabulate(rows, headers=headers, tablefmt='simple')


def list_apps(session: Session, endpoint: str, id_only: bool) -> str:
    apps = get_custom_apps_list(session, endpoint)

    if id_only:
        return '\n'.join([app['id'] for app in apps])

    headers = ['id', 'name', 'status', 'applicationUrl']
    return format_table(apps, headers)


def list_environments(session: Session, endpoint: str, id_only: bool) -> str:
    envs = get_execution_environments_list(session, endpoint)

    if id_only:
        return '\n'.join([ee['id'] for ee in envs])

    headers = ['id', 'name', 'description']
    return format_table(envs, headers)


@click.command()
@api_token
@api_endpoint
@click.option('--id-only', is_flag=True, show_default=True, default=False, help='Output only ids')
@click.argument('entity', type=click.Choice(['apps', 'envs']))
def ls(token: str, endpoint: str, id_only: bool, entity: str) -> None:
    """Provide list of custom applications or execution environments."""
    session = Session()
    session.headers.update({'Authorization': f'Bearer {token}'})

    if entity == 'apps':
        output = list_apps(session, endpoint, id_only)
    else:
        output = list_environments(session, endpoint, id_only)
    click.echo(output)
