#
#  Copyright 2024 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
import json

import pytest
import responses
from bson import ObjectId
from click.testing import CliRunner
from responses import matchers

from drapps.terminate import terminate


@responses.activate
@pytest.mark.parametrize('use_name', (False, True))
def test_terminate(api_endpoint_env, api_token_env, use_name):
    app_id = str(ObjectId())
    app_name = 'app_name'

    # checker for API token
    auth_matcher = matchers.header_matcher({'Authorization': f'Bearer {api_token_env}'})
    if use_name:
        app_list_url = f'{api_endpoint_env}/customApplications/'
        # check that name filter was used
        params_matcher = matchers.query_param_matcher({'name': app_name})
        responses.get(
            app_list_url,
            json={'count': 1, 'data': [{'id': app_id, 'name': app_name}]},
            match=[auth_matcher, params_matcher],
        )

    app_url = f'{api_endpoint_env}/customApplications/{app_id}/'
    responses.delete(app_url, status=204, match=[auth_matcher])

    identifier = app_name if use_name else app_id

    runner = CliRunner()
    result = runner.invoke(terminate, [identifier])
    assert result.exit_code == 0, result.exception
    assert result.output == f'Custom application {identifier} was deleted.\n'


@responses.activate
@pytest.mark.usefixtures('api_token_env')
@pytest.mark.parametrize('from_input_stream', (False, True))
def test_terminate_list(api_endpoint_env, from_input_stream):
    applications = {'App_1': str(ObjectId()), 'App_2': str(ObjectId()), 'App_3': str(ObjectId())}

    def request_callback(request):
        app_name = request.params['name']
        app_id = applications[app_name]
        resp_body = {'count': 1, 'data': [{'id': app_id, 'name': app_name}]}
        return 200, {}, json.dumps(resp_body)

    responses.add_callback(
        responses.GET,
        f'{api_endpoint_env}/customApplications/',
        callback=request_callback,
        content_type="application/json",
    )

    for app_id in applications.values():
        responses.delete(f'{api_endpoint_env}/customApplications/{app_id}/', status=204)

    runner = CliRunner()

    if from_input_stream:
        # provide names through stdin to imitate shell pipes
        input_stream = ''.join(f'{key}\n' for key in applications.keys())
        params = {'input': input_stream}
    else:
        # provide names as command arguments
        params = {'args': list(applications.keys())}

    result = runner.invoke(terminate, **params)
    assert result.exit_code == 0, result.exception

    expected_output = ''.join(
        [f'Custom application {app_name} was deleted.\n' for app_name in applications.keys()]
    )
    assert result.output == expected_output


@responses.activate
@pytest.mark.usefixtures('api_token_env')
def test_terminate_handle_errors(api_endpoint_env):
    call_params = ['659eec8f2522de35c1b2c8a6', 'wrong_name', '659eec492522de2b78175c01']

    # app does not exist
    responses.delete(f'{api_endpoint_env}/customApplications/659eec8f2522de35c1b2c8a6/', status=404)
    # no app with such name
    responses.get(
        f'{api_endpoint_env}/customApplications/?name=wrong_name', json={'count': 0, 'data': []}
    )
    # no permissions for deleting this app
    responses.delete(f'{api_endpoint_env}/customApplications/659eec492522de2b78175c01/', status=403)

    runner = CliRunner()
    result = runner.invoke(terminate, call_params)

    expected_output = (
        'Cannot find application 659eec8f2522de35c1b2c8a6.\n'
        'Cannot find application wrong_name.\n'
        'No permissions for deleting 659eec492522de2b78175c01.\n'
    )
    assert result.output == expected_output
