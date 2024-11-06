#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
from datetime import datetime
from functools import partial
from typing import Any, Callable, Dict, List

import click
from dateutil import parser
from requests import Session
from tabulate import tabulate

from .helpers.custom_apps_functions import get_custom_apps_list
from .helpers.execution_environments_functions import get_execution_environments_list
from .helpers.wrappers import api_endpoint, api_token


def _string_fetcher(field_name: str, entity) -> str:
    return entity.get(field_name)


def _date_fetcher(field_name: str, entity) -> str:
    str_date = entity.get(field_name)
    if not str_date:
        return ''

    date = parser.parse(str_date)
    if date.date() == datetime.today().date():
        # if it was today, return just time
        return date.strftime('%H:%M:%S')
    else:
        return date.date().isoformat()


def _list_str_fetcher(field_name: str, entity) -> str:
    return ','.join(entity.get(field_name))


def format_table(
    data: List[Dict[str, Any]], data_fetchers: Dict[str, Callable[[Dict[str, Any]], str]]
) -> str:
    headers = list(data_fetchers.keys())
    rows = []
    for element in data:
        rows.append([data_fetchers[column](element) for column in headers])
    return tabulate(rows, headers=headers, tablefmt='simple')


def list_apps(session: Session, endpoint: str, id_only: bool) -> str:
    apps = get_custom_apps_list(session, endpoint)

    if id_only:
        return '\n'.join([app['id'] for app in apps])

    data_fetchers = {
        'id': partial(_string_fetcher, 'id'),
        'name': partial(_string_fetcher, 'name'),
        'status': partial(_string_fetcher, 'status'),
        'updated': partial(_date_fetcher, 'updatedAt'),
        'URL': partial(_string_fetcher, 'applicationUrl'),
        'external sharing': partial(_string_fetcher, 'externalAccessEnabled'),
        'external sharing recipients': partial(_list_str_fetcher, 'externalAccessRecipients'),
    }
    return format_table(apps, data_fetchers)  # type: ignore[arg-type]


def list_environments(session: Session, endpoint: str, id_only: bool) -> str:
    envs = get_execution_environments_list(session, endpoint)

    if id_only:
        return '\n'.join([ee['id'] for ee in envs])

    data_fetchers = {
        'id': partial(_string_fetcher, 'id'),
        'name': partial(_string_fetcher, 'name'),
        'description': partial(_string_fetcher, 'description'),
    }
    return format_table(envs, data_fetchers)  # type: ignore[arg-type]


@click.command()
@api_token
@api_endpoint
@click.option('--id-only', is_flag=True, show_default=True, default=False, help='Output only ids')
@click.argument('entity', type=click.Choice(['apps', 'envs']))
def ls(token: str, endpoint: str, id_only: bool, entity: str) -> None:
    """Provides list of custom applications or execution environments."""
    session = Session()
    session.headers.update({'Authorization': f'Bearer {token}'})

    if entity == 'apps':
        output = list_apps(session, endpoint, id_only)
    else:
        output = list_environments(session, endpoint, id_only)
    click.echo(output)
