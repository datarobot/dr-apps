#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#


class ClientResponseError(Exception):
    def __init__(self, url: str, status: int, message: str):
        self.url = url
        self.status = status
        self.message = message

    def __str__(self) -> str:
        return f'{self.status}, message={self.message}, url={self.url}'
