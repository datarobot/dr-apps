#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
from time import sleep
from typing import Any, Dict

import click
from bson import ObjectId
from requests import Session

from .helpers.custom_apps_functions import get_custom_app_by_name, get_custom_app_logs
from .helpers.wrappers import api_endpoint, api_token

SLEEP_TIME = 30


def _format_runtime_logs(app_logs: Dict[str, Any]) -> str:
    runtime_logs = app_logs.get('logs')
    if not runtime_logs:
        return ''
    return '\n'.join(runtime_logs)


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
    """Provides logs for custom application."""
    session = Session()
    session.headers.update({'Authorization': f'Bearer {token}'})

    if ObjectId.is_valid(application_id_or_name):
        app_id = application_id_or_name
    else:
        app = get_custom_app_by_name(session, endpoint, app_name=application_id_or_name)
        app_id = app['id']

    app_logs = get_custom_app_logs(session, endpoint, app_id)
    runtime_logs = _format_runtime_logs(app_logs)

    if not runtime_logs and not follow:
        # it looks like we cant find any runtimes logs, lets try to show image build logs
        image_build_error = app_logs.get('buildError')
        image_build_logs = app_logs.get('buildLog')

        if not (image_build_error or image_build_logs):
            click.echo('This app currently has no logs.')
            return

        if image_build_error:
            click.echo(f'Dependency image build error: {image_build_error}')
        if image_build_logs:
            click.echo(f'Dependency image build log:\n{image_build_logs}')
        return

    click.echo(runtime_logs, nl=False)

    while follow:
        sleep(SLEEP_TIME)
        new_logs = _format_runtime_logs(get_custom_app_logs(session, endpoint, app_id))
        if new_logs != runtime_logs:
            click.echo(new_logs[len(runtime_logs) :], nl=False)
            runtime_logs = new_logs

    click.echo()
