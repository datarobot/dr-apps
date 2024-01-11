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

    def wrapper(*args, **kwargs) -> None:
        if not kwargs.get('token'):
            token = os.environ.get('DATAROBOT_API_TOKEN')
            if not token:
                raise ValueError(
                    'You need to set DR API token through parameters or DATAROBOT_API_TOKEN env variable.'
                )
            kwargs['token'] = token

        command(*args, **kwargs)

    for attr in MIMIC_ATTRIBUTES:
        if hasattr(command, attr):
            setattr(wrapper, attr, getattr(command, attr))
    option_wrapper = click.option(
        '-t', '--token', type=click.STRING, help='Pubic API access token.'
    )
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
    option_wrapper = click.option(
        '-E', '--endpoint', type=click.STRING, help='Data Robot Public API endpoint.'
    )
    return option_wrapper(wrapper)
