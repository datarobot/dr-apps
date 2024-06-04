#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
import logging
from unittest.mock import patch

import pytest
import responses
from bson import ObjectId
from click.testing import CliRunner
from responses import matchers

from drapps.env import create_env


@responses.activate
@pytest.mark.parametrize('image_name', ['dockerfile.tgz'])
@pytest.mark.parametrize('env_name', ["My New Execution Env"])
@pytest.mark.parametrize('description', ["This is an Exec Env", None] )
def test_create_env_with_version(api_endpoint_env, api_token_env, image_name, description, env_name):
    execution_environments_id = ObjectId()
    auth_matcher = matchers.header_matcher(
        {'Authorization': f'Bearer {api_token_env}'}
    )  # checker for API token

    # setup + test execution env
    exec_env_url = f'{api_endpoint_env}/executionEnvironments/'
    exec_env_matcher = {
        'name': env_name,
        'useCases': ['customApplication'],
    }
    if description is not None:
        exec_env_matcher['description'] = description
    responses.post(exec_env_url, json={'id': str(execution_environments_id)}, match=[auth_matcher, matchers.json_params_matcher(exec_env_matcher)])

    # setup + test version
    exec_env_version_url = f'{api_endpoint_env}/executionEnvironments/{execution_environments_id}/versions/'
    version_id = str(ObjectId())
    responses.post(exec_env_version_url, json={'id': version_id}, match=[auth_matcher])

    exec_env_version_status_url = f'{api_endpoint_env}/executionEnvironments/{execution_environments_id}/versions/{version_id}/'
    exec_env_version_rsp = {
        "buildStatus": "success",
    }
    responses.get(exec_env_version_status_url, json=exec_env_version_rsp, match=[auth_matcher])

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(image_name, 'wb') as image_file:
            image_file.write(b'Some data')

        with patch('drapps.create.CHECK_STATUS_WAIT_TIME', 0):
            result = runner.invoke(create_env, ["--name", env_name, "-i", image_name, '-d', description])
    logger = logging.getLogger()
    if result.exit_code:
        logger.error(result.output)
    else:
        logger.info(result.output)
    assert result.exit_code == 0, result.exception
