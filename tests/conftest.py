#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#

import pytest


@pytest.fixture
def api_endpoint():
    return 'https://api.test.com/api/v2'


@pytest.fixture
def api_endpoint_env(monkeypatch, api_endpoint):
    with monkeypatch.context() as mp:
        mp.setenv('DATAROBOT_ENDPOINT', api_endpoint)
        yield api_endpoint


@pytest.fixture
def api_token():
    return 'THIS_IS_API_TOKEN'


@pytest.fixture
def api_token_env(monkeypatch, api_token):
    with monkeypatch.context() as mp:
        mp.setenv('DATAROBOT_API_TOKEN', api_token)
        yield api_token
