#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
from time import sleep

import click
from bson import ObjectId
from requests import Session

from .helpers.custom_apps_functions import get_custom_app_logs, get_custom_app_by_name
from .helpers.wrappers import api_endpoint, api_token

SLEEP_TIME = 30


@click.command()
@api_token
@api_endpoint
@click.option(
    '-f',
    '--follow',
    is_flag=True,
    show_default=True,
    default=False,
    help='Output append data as new log records appear.',
)
@click.argument('application_id_or_name', type=click.STRING)
def logs(token: str, endpoint: str, follow: bool, application_id_or_name: str) -> None:
    """Provide logs for custom application."""
    session = Session()
    session.headers.update({'Authorization': f'Bearer {token}'})

    if ObjectId.is_valid(application_id_or_name):
        app_id = application_id_or_name
    else:
        app = get_custom_app_by_name(session, endpoint, app_name=application_id_or_name)
        app_id = app['id']

    app_logs = get_custom_app_logs(session, endpoint, app_id)
    click.echo(app_logs, nl=False)

    while follow:
        sleep(SLEEP_TIME)
        new_logs = get_custom_app_logs(session, endpoint, app_id)
        if new_logs != app_logs:
            click.echo(new_logs[len(app_logs) :], nl=False)
            app_logs = new_logs

    click.echo()
