#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#

from typing import Dict, Optional


class ClientResponseError(Exception):
    def __init__(
        self, url: str, status: int, message: str, errors: Optional[Dict[str, str]] = None
    ):
        self.url = url
        self.status = status
        self.message = message
        self.errors = errors

    def __str__(self) -> str:
        if self.errors:
            return f'{self.status}, message={self.message}, url={self.url}, errors={self.errors}'
        return f'{self.status}, message={self.message}, url={self.url}'
