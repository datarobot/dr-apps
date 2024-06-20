#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
from unittest.mock import patch

import pytest
import responses
from bson import ObjectId
from click.testing import CliRunner
from responses import matchers

from drapps.logs import logs


@responses.activate
@pytest.mark.parametrize('use_name', (False, True))
@pytest.mark.parametrize('image_build_failed', (False, True))
def test_logs(api_endpoint_env, api_token_env, use_name, image_build_failed):
    app_id = str(ObjectId())
    app_name = 'app_name'

    auth_matcher = matchers.header_matcher(
        {'Authorization': f'Bearer {api_token_env}'}
    )  # checker for API token
    if use_name:
        app_list_url = f'{api_endpoint_env}/customApplications/'
        params_matcher = matchers.query_param_matcher(
            {'name': app_name}
        )  # check that name filter was used
        responses.get(
            app_list_url,
            json={'count': 1, 'data': [{'id': app_id, 'name': app_name}]},
            match=[auth_matcher, params_matcher],
        )

    app_logs = 'here is some logs'
    build_error = 'here is some build error'
    build_logs = 'here is some build logs'
    if image_build_failed:
        logs_payload = {'logs': [], 'buildError': build_error, 'buildLog': build_logs}
        expected_output = (
            f'Dependency image build error: {build_error}\n'
            f'Dependency image build log:\n{build_logs}\n'
        )
    else:
        logs_payload = {'logs': [app_logs], 'buildError': '', 'buildLogs': build_logs}
        expected_output = app_logs + '\n'

    logs_url = f'{api_endpoint_env}/customApplications/{app_id}/logs/'
    responses.get(logs_url, json=logs_payload, match=[auth_matcher])

    identifier = app_name if use_name else app_id

    runner = CliRunner()
    result = runner.invoke(logs, [identifier])
    assert result.exit_code == 0, result.exception
    assert result.output == expected_output


@responses.activate
def test_logs_with_wrong_app_name(api_endpoint_env, api_token_env):
    app_name = 'wrong_name'

    app_list_url = f'{api_endpoint_env}/customApplications/'
    auth_matcher = matchers.header_matcher(
        {'Authorization': f'Bearer {api_token_env}'}
    )  # checker for API token
    params_matcher = matchers.query_param_matcher(
        {'name': app_name}
    )  # check that name filter was used
    # no apps in response
    responses.get(app_list_url, json={'count': 0, 'data': []}, match=[auth_matcher, params_matcher])

    runner = CliRunner()
    result = runner.invoke(logs, [app_name])
    assert result.exit_code == 1
    expected_error = f'404, message=Can\'t find custom application "{app_name}" by name., url={api_endpoint_env}/customApplications/'
    assert str(result.exception) == expected_error


@responses.activate
@pytest.mark.usefixtures('api_token_env')
def test_logs_with_follow(api_endpoint_env):
    app_id = str(ObjectId())

    logs_url = f'{api_endpoint_env}/customApplications/{app_id}/logs/'

    log_1 = 'First log line.\n'
    log_2 = 'Second log line.\n'

    responses.get(logs_url, json={'logs': [log_1]})  # mock for the first call
    responses.get(logs_url, json={'logs': [log_1 + log_2]})  # mock for the second call
    responses.get(
        logs_url, body=KeyboardInterrupt()
    )  # imitation CTRL+C during third request for exiting from follow

    runner = CliRunner()
    with patch('drapps.logs.SLEEP_TIME', 0):
        result = runner.invoke(logs, ['-f', app_id])

    assert result.output == log_1 + log_2
