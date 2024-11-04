from typing import Any, List, Optional

import click
from bson import ObjectId
from requests import Session

from .helpers.custom_apps_functions import (
    get_custom_app_by_id,
    get_custom_app_by_name,
    update_running_custom_app,
)
from .helpers.wrappers import api_endpoint, api_token


@click.command()
@api_token
@api_endpoint
@click.argument('application_name', type=click.STRING, required=True)
@click.option('--set-external-sharing', type=click.BOOL, default=None)
@click.option(
    '--add-external-user',
    multiple=True,
    required=False,
    type=click.STRING,
)
@click.option(
    '--remove-external-user',
    multiple=True,
    required=False,
    type=click.STRING,
)
def external_share(
    token: str,
    endpoint: str,
    set_external_sharing: Optional[bool],
    application_name: str,
    add_external_user: List[str],
    remove_external_user: List[str],
):
    session = Session()
    session.headers.update({'Authorization': f'Bearer {token}'})
    payload: dict[str, Any] = dict()
    if ObjectId.is_valid(application_name):
        app = get_custom_app_by_id(session, endpoint, app_id=application_name)
        app_id = application_name
    else:
        app = get_custom_app_by_name(session, endpoint, app_name=application_name)
        app_id = app['id']

    if set_external_sharing is not None:
        payload['externalAccessEnabled'] = set_external_sharing
    if add_external_user or remove_external_user:
        current_external_users = set(app.get('externalAccessRecipients', []))
        if add_external_user:
            current_external_users.update(set(add_external_user))
        if remove_external_user:
            current_external_users.difference_update(set(remove_external_user))
        payload['externalAccessRecipients'] = list(current_external_users)

    update_running_custom_app(
        session=session,
        app_id=app_id,
        endpoint=endpoint,
        payload=payload,
    )
