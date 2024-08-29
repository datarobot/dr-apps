#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#

import pytest
from bson import ObjectId


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


@pytest.fixture
def ee_id():
    return str(ObjectId())


@pytest.fixture
def ee_last_version_id():
    return str(ObjectId())


@pytest.fixture
def string_env_vars():
    return {'FOO': 'BAR', 'API_KEY': '1234abcd'}


@pytest.fixture
def numeric_env_vars():
    return {'MAX_RETRIES': 3, 'TIMEOUT': 60}


@pytest.fixture
def metadata_yaml_content():
    return """
    runtimeParameterDefinitions:
      - fieldName: FOO
        type: string
      - fieldName: API_KEY
        type: string
      - fieldName: MAX_RETRIES
        type: numeric
      - fieldName: TIMEOUT
        type: numeric
    """


@pytest.fixture
def entrypoint_script_content():
    return '#!/usr/bin/env bash\necho "We doing here something"'
