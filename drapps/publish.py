#
#  Copyright 2024 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
from typing import Optional

import click
from bson import ObjectId
from requests import Session

from drapps.helpers.custom_apps_functions import (
    get_custom_app_by_id,
    get_custom_app_by_name,
    get_history_by_index,
    update_running_custom_app,
    wait_for_app_to_be_running,
)
from drapps.helpers.wrappers import api_endpoint, api_token


@click.command()
@api_token
@api_endpoint
@click.option(
    '-i',
    '--application-to-be-updated',
    required=True,
    type=click.STRING,
    help='Name or ID for the application to update.',
)
@click.option(
    '-n',
    '--name',
    required=False,
    type=click.STRING,
    help='New name for the application',
)
@click.option(
    '-s',
    '--source-application',
    required=False,
    type=click.STRING,
    help='Name or ID for the application to copy the application from.',
)
@click.option(
    '--skip-wait',
    is_flag=True,
    show_default=True,
    default=False,
    help='Do not wait for ready status.',
)
def publish(
    application_to_be_updated: str,
    token: str,
    endpoint: str,
    name: Optional[str],
    source_application: Optional[str],
    skip_wait: bool,
) -> None:
    """Updates a custom app, this covers the basic case of a new name
    and also the custom apps publishing work which is scoped for 10.2
    """
    session = Session()
    session.headers.update({'Authorization': f'Bearer {token}'})
    payload = {}
    if ObjectId.is_valid(application_to_be_updated):
        app_id = application_to_be_updated
    else:
        app = get_custom_app_by_name(session, endpoint, app_name=application_to_be_updated)
        app_id = app['id']

    if source_application:
        if ObjectId.is_valid(source_application):
            app = get_custom_app_by_id(session, endpoint, source_application)
        else:
            app = get_custom_app_by_name(session, endpoint, app_name=source_application)
        payload['customApplicationSourceVersionId'] = app['customApplicationSourceVersionId']

    if name:
        payload['name'] = name
    update_running_custom_app(
        session=session,
        app_id=app_id,
        endpoint=endpoint,
        payload=payload,
    )
    if not skip_wait:
        wait_for_app_to_be_running(
            session=session,
            app_id=app_id,
            endpoint=endpoint,
        )


@click.command()
@api_token
@api_endpoint
@click.option(
    '-i',
    '--application-to-be-updated',
    required=True,
    type=click.STRING,
    help='Name or ID for the application to update.',
)
@click.option(
    '-b',
    '--by',
    required=True,
    type=click.INT,
    help='How many versions back you are going',
)
@click.option(
    '--skip-wait',
    is_flag=True,
    show_default=True,
    default=False,
    help='Do not wait for ready status.',
)
def revert_publish(
    token: str,
    endpoint: str,
    by: int,
    application_to_be_updated: str,
    skip_wait: bool,
):
    session = Session()
    session.headers.update({'Authorization': f'Bearer {token}'})
    if ObjectId.is_valid(application_to_be_updated):
        app_id = application_to_be_updated
    else:
        app = get_custom_app_by_name(session, endpoint, app_name=application_to_be_updated)
        app_id = app['id']
    history = get_history_by_index(
        session=session,
        app_id=app_id,
        endpoint=endpoint,
        index=by - 1,
    )

    update_running_custom_app(
        session=session,
        app_id=app_id,
        endpoint=endpoint,
        payload={'customApplicationSourceVersionId': history['sourceVersionId']},
    )
    if not skip_wait:
        wait_for_app_to_be_running(
            session=session,
            endpoint=endpoint,
            app_id=app_id,
        )
