#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
from requests import JSONDecodeError, Response

from .exceptions import ClientResponseError


def handle_dr_response(response: Response, raise_error: bool = True) -> None:
    """
    Helper function which allows unified handling of all DataRobot responses.
    """
    if 400 <= response.status_code:
        assert response.reason  # always not None for started response
        try:
            data = response.json()
            message = data.get('message', response.reason)
            errors = data.get('errors', None)
        except JSONDecodeError:
            message = response.reason
            errors = None
        exception = ClientResponseError(
            url=response.url, status=response.status_code, message=message, errors=errors
        )
        if raise_error:
            raise exception
