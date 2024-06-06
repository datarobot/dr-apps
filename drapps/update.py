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

from drapps.helpers.custom_apps_functions import get_custom_app_by_name, update_running_custom_app
from drapps.helpers.wrappers import api_endpoint, api_token
from drapps.terminate import RequiredStringsFromParamsAndStdin


@click.command()
@api_token
@api_endpoint
@click.option(
    '-i',
    '--application-id-or-name',
    required=False,
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
    '--source-application-id-or-name',
    required=False,
    type=click.STRING,
    help='Name or ID for the application to copy the application from.',
)
def update(
    application_id_or_name: str,
    token: str,
    endpoint: str,
    name: Optional[str],
    source_application_id_or_name: Optional[str],
) -> None:
    """Updates a custom app, this covers the basic case of a new name
    and also the custom apps publishing work which is scoped for 10.2
    """
    session = Session()
    source_application_id = None
    session.headers.update({'Authorization': f'Bearer {token}'})
    payload = {}
    if ObjectId.is_valid(application_id_or_name):
        app_id = application_id_or_name
    else:
        app = get_custom_app_by_name(session, endpoint, app_name=application_id_or_name)
        app_id = app['id']

    if source_application_id_or_name:
        if ObjectId.is_valid(source_application_id_or_name):
            source_application_id = source_application_id_or_name
        else:
            app = get_custom_app_by_name(session, endpoint, app_name=source_application_id_or_name)
            source_application_id = app['id']
    if name:
        payload['name'] = name
    if source_application_id:
        payload['sourceApplicationId'] = source_application_id
    update_running_custom_app(
        session=session,
        app_id=app_id,
        endpoint=endpoint,
        payload=payload,
    )
