#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
import os
import posixpath
from typing import Callable

import click

MIMIC_ATTRIBUTES = ['__click_params__', '__name__', '__doc__']


def api_token(command: Callable[..., None]) -> Callable[..., None]:
    """Attaches a token option to the command with possibility to set up this option from ENV variables"""
    name = 'token'
    short = 't'

    def wrapper(*args, **kwargs) -> None:
        if not kwargs.get(name):
            token = os.environ.get('DATAROBOT_API_TOKEN')
            if not token:
                raise click.MissingParameter(
                    'You need to set DR API token through parameters or DATAROBOT_API_TOKEN env variable.',
                    param_hint=f'-{short}/--{name}',
                    param_type='option',
                )
            kwargs[name] = token

        command(*args, **kwargs)

    for attr in MIMIC_ATTRIBUTES:
        if hasattr(command, attr):
            setattr(wrapper, attr, getattr(command, attr))

    help_text = 'Pubic API access token. You can use DATAROBOT_API_TOKEN env instead.'
    option_wrapper = click.option(f'--{name}', f'-{short}', type=click.STRING, help=help_text)
    return option_wrapper(wrapper)


def api_endpoint(command: Callable[..., None]) -> Callable[..., None]:
    """Attaches an endpoint option to the command with possibility to set up this option from ENV variables"""

    def wrapper(*args, **kwargs) -> None:
        if not kwargs.get('endpoint'):
            dr_host = os.environ.get('DATAROBOT_HOST', 'https://app.datarobot.com')
            endpoint = os.environ.get('DATAROBOT_ENDPOINT', posixpath.join(dr_host, 'api/v2'))
            kwargs['endpoint'] = endpoint

        command(*args, **kwargs)

    for attr in MIMIC_ATTRIBUTES:
        if hasattr(command, attr):
            setattr(wrapper, attr, getattr(command, attr))

    help_text = (
        'Data Robot Public API endpoint. You can use DATAROBOT_ENDPOINT instead. '
        'Default: https://app.datarobot.com/api/v2'
    )
    option_wrapper = click.option('-E', '--endpoint', type=click.STRING, help=help_text)
    return option_wrapper(wrapper)
