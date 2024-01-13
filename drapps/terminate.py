#
#  Copyright 2024 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
import sys
from typing import Any, Tuple

import click
from bson import ObjectId
from requests import Session

from .helpers.custom_apps_functions import delete_custom_app, get_custom_app_by_name
from .helpers.exceptions import ClientResponseError
from .helpers.wrappers import api_endpoint, api_token


def remove_app(session: Session, endpoint: str, application_id_or_name: str):
    if ObjectId.is_valid(application_id_or_name):
        app_id = application_id_or_name
    else:
        app = get_custom_app_by_name(session, endpoint, app_name=application_id_or_name)
        app_id = app['id']

    delete_custom_app(session, endpoint, app_id)


class RequiredStringsFromParamsAndStdin(click.Argument):
    """
    Custom argument that tries getting value from parameters and if fails,
    try to read from stdin stream.
    """

    def __init__(self, *args, **kwargs):
        kwargs['nargs'] = -1
        kwargs['type'] = click.STRING
        kwargs['required'] = True
        super().__init__(*args, **kwargs)

    def process_value(self, ctx: click.Context, value: Any) -> Any:
        value = self.type_cast_value(ctx, value)

        if self.value_is_missing(value) and not sys.stdin.isatty():
            # if we have no value but sys.stdin attached to file
            # we make a try to read from file
            stdin_text = click.get_text_stream('stdin')
            value = tuple(line.strip() for line in stdin_text.readlines())

        if self.value_is_missing(value):
            raise click.MissingParameter(ctx=ctx, param=self)

        if self.callback is not None:
            value = self.callback(ctx, self, value)

        return value


@click.command()
@api_token
@api_endpoint
@click.argument("application_id_or_name", cls=RequiredStringsFromParamsAndStdin)
def terminate(token: str, endpoint: str, application_id_or_name: Tuple[str]) -> None:
    """Stops custom application and removes it from the list."""
    session = Session()
    session.headers.update({'Authorization': f'Bearer {token}'})

    for app_id_name in application_id_or_name:
        try:
            remove_app(session, endpoint, app_id_name)
        except ClientResponseError as error:
            if error.status == 404:
                click.echo(f'Cannot find application {app_id_name}.', err=True)
            elif error.status == 403:
                click.echo(f'No permissions for deleting {app_id_name}.', err=True)
            else:
                raise error
        else:
            click.echo(f'Custom application {app_id_name} was deleted.')
