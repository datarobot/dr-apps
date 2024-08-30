#
#  Copyright 2024 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
import json
from pathlib import Path
from unittest.mock import patch

import pytest
import responses
from bson import ObjectId
from click.testing import CliRunner
from responses import matchers

from drapps.create import create


@responses.activate
@pytest.mark.parametrize('wait_till_ready', (False, True))
def test_create_from_docker_image(api_endpoint_env, api_token_env, wait_till_ready):
    app_name = 'new_app'
    image_name = 'image.tar'

    auth_matcher = matchers.header_matcher(
        {'Authorization': f'Bearer {api_token_env}'}
    )  # checker for API token

    # request for checking if name is unique
    name_matcher = matchers.query_param_matcher({'name': app_name})
    responses.get(
        f'{api_endpoint_env}/customApplications/nameCheck/',
        json={'inUse': False},
        match=[auth_matcher, name_matcher],
    )

    # request for creating new execution environment
    ee_environment_id = str(ObjectId())
    ee_data_matcher = matchers.json_params_matcher(
        {
            'name': image_name,
            'useCases': ['customApplication'],
            'description': 'Environment for prebuild image with a custom application.',
        }
    )
    responses.post(
        f'{api_endpoint_env}/executionEnvironments/',
        json={'id': ee_environment_id},
        match=[auth_matcher, ee_data_matcher],
    )

    # request for uploading docker image to execution environment version
    ee_environment_version_id = str(ObjectId())
    responses.post(
        f'{api_endpoint_env}/executionEnvironments/{ee_environment_id}/versions/',
        json={'id': ee_environment_version_id},
        match=[auth_matcher],
    )
    # requests for checking image readiness
    ee_environment_version_url = f'{api_endpoint_env}/executionEnvironments/{ee_environment_id}/versions/{ee_environment_version_id}/'
    responses.get(
        ee_environment_version_url, json={'buildStatus': 'processing'}, match=[auth_matcher]
    )
    responses.get(ee_environment_version_url, json={'buildStatus': 'success'}, match=[auth_matcher])

    # request for creating custom app
    status_check_url = 'http://ho.st/status/status_id'
    app_data_matcher = matchers.json_params_matcher(
        {'name': app_name, 'environmentId': ee_environment_id}
    )
    custom_app_response = {
        'id': str(ObjectId()),
        'applicationUrl': 'http://ho.st/custom_applications/65980d79eea4fd0eddd59bba/',
    }
    responses.post(
        f'{api_endpoint_env}/customApplications/',
        headers={'Location': status_check_url},
        json=custom_app_response,
        match=[auth_matcher, app_data_matcher],
    )

    if wait_till_ready:
        # request for checking app startup status
        responses.get(status_check_url, json={'status': 'RUNNING'}, match=[auth_matcher])
        responses.get(status_check_url, json={'status': 'COMPLETED'}, match=[auth_matcher])

    expected_output = (
        f'Uploading {image_name} to Data Robot.\n'
        'Upload progress:\n'
        'Waiting till image is ready:\n'
        f'Starting {app_name} custom application.\n'
    )
    if wait_till_ready:
        expected_output += (
            'Waiting till app is ready:\n'
            'Custom application is running: http://ho.st/custom_applications/65980d79eea4fd0eddd59bba/\n'
        )
    else:
        expected_output += f'Custom application {app_name} was successfully created.\n'

    cli_parameters = ['--image', image_name, app_name]
    if not wait_till_ready:
        cli_parameters.append('--skip-wait')

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(image_name, 'wb') as image_file:
            image_file.write(b'Some data')

        with patch('drapps.create.CHECK_STATUS_WAIT_TIME', 0):
            result = runner.invoke(create, cli_parameters)

    assert result.exit_code == 0, result.exception
    assert result.output == expected_output


@responses.activate
@pytest.mark.parametrize('use_environment_id', (False, True))
@pytest.mark.parametrize('wait_till_ready', (False, True))
def test_create_from_project(
    api_endpoint_env,
    api_token_env,
    ee_id,
    ee_last_version_id,
    string_env_vars,
    numeric_env_vars,
    metadata_yaml_content,
    entrypoint_script_content,
    use_environment_id,
    wait_till_ready,
):
    app_name = 'new_app'
    project_folder = 'project-folder'
    ee_name = 'ExecutionEnv'

    auth_matcher = matchers.header_matcher(
        {'Authorization': f'Bearer {api_token_env}'}
    )  # checker for API token

    # request for checking if name is unique
    name_matcher = matchers.query_param_matcher({'name': app_name})
    responses.get(
        f'{api_endpoint_env}/customApplications/nameCheck/',
        json={'inUse': False},
        match=[auth_matcher, name_matcher],
    )

    # request for fetching execution environment data
    ee_data = {'id': ee_id, 'name': ee_name, 'latestVersion': {'id': ee_last_version_id}}
    if use_environment_id:
        responses.get(
            f'{api_endpoint_env}/executionEnvironments/{ee_id}/', json=ee_data, match=[auth_matcher]
        )
    else:
        params_matcher = matchers.query_param_matcher(
            {'useCases': 'customApplication', 'searchFor': ee_name}
        )
        responses.get(
            f'{api_endpoint_env}/executionEnvironments/',
            json={'data': [ee_data]},
            match=[auth_matcher, params_matcher],
        )

    # request for checking if custom app source exists
    responses.get(
        f'{api_endpoint_env}/customApplicationSources/', json={'data': []}, match=[auth_matcher]
    )
    # request for creating new application source
    custom_app_source_id = str(ObjectId())
    source_data_matcher = matchers.json_params_matcher({'name': f'{app_name}Source'})
    responses.post(
        f'{api_endpoint_env}/customApplicationSources/',
        json={'id': custom_app_source_id},
        match=[auth_matcher, source_data_matcher],
    )
    # request for creating new application source version
    custom_app_source_version_id = str(ObjectId())
    source_version_data_matcher = matchers.json_params_matcher({'label': 'v1'})
    responses.post(
        f'{api_endpoint_env}/customApplicationSources/{custom_app_source_id}/versions/',
        json={'id': custom_app_source_version_id},
        match=[auth_matcher, source_version_data_matcher],
    )

    responses.patch(
        f'{api_endpoint_env}/customApplicationSources/{custom_app_source_id}/versions/{custom_app_source_version_id}/',
    )

    # request for creating custom app
    status_check_url = 'http://ho.st/status/status_id'
    app_data_matcher = matchers.json_params_matcher(
        {'name': app_name, 'applicationSourceId': custom_app_source_id}
    )
    custom_app_response = {
        'id': str(ObjectId()),
        'applicationUrl': 'http://ho.st/custom_applications/65980d79eea4fd0eddd59bba/',
    }
    responses.post(
        f'{api_endpoint_env}/customApplications/',
        headers={'Location': status_check_url},
        json=custom_app_response,
        match=[auth_matcher, app_data_matcher],
    )

    if wait_till_ready:
        # request for checking app startup status
        responses.get(status_check_url, json={'status': 'RUNNING'}, match=[auth_matcher])
        responses.get(status_check_url, json={'status': 'COMPLETED'}, match=[auth_matcher])

    expected_output = (
        f'Using {app_name}Source custom application source.\n'
        f'Creating new version for {app_name}Source custom application source.\n'
        'Uploading project:\n'
        'Starting new_app custom application.\n'
    )
    if wait_till_ready:
        expected_output += (
            'Waiting till app is ready:\n'
            'Custom application is running: http://ho.st/custom_applications/65980d79eea4fd0eddd59bba/\n'
        )
    else:
        expected_output += f'Custom application {app_name} was successfully created.\n'

    environment_identifier = ee_id if use_environment_id else ee_name
    cli_parameters = [
        '--base-env',
        environment_identifier,
        '--path',
        project_folder,
        app_name,
        '--stringEnvVar',
        'FOO=BAR',
        '--stringEnvVar',
        'API_KEY=Random API Key',
        '--numericEnvVar',
        'INT_VAL=3',
        '--numericEnvVar',
        'FLOAT_VAL=3.14',
    ]
    if not wait_till_ready:
        cli_parameters.append('--skip-wait')

    runner = CliRunner()
    with runner.isolated_filesystem():
        # imitating project by creation folder and start script
        Path(project_folder).mkdir()
        with Path(project_folder, 'start-app.sh').open('w') as script_file:
            script_file.write(entrypoint_script_content)
        with Path(project_folder, 'metadata.yaml').open('w') as meta_file:
            meta_file.write(metadata_yaml_content)

        with patch('drapps.create.CHECK_STATUS_WAIT_TIME', 0):
            result = runner.invoke(create, cli_parameters)

    assert result.exit_code == 0, result.exception
    assert result.output == expected_output

    # Add assertions to check if the environment variables were correctly passed
    assert len(responses.calls) > 0
    env_var_requests = [
        call
        for call in responses.calls
        if call.request.url.endswith(f'/versions/{custom_app_source_version_id}/')
        and call.request.method == 'PATCH'
        and 'runtimeParameterValues' in call.request.body.decode('utf-8')
    ]

    assert len(env_var_requests) == len(string_env_vars) + len(numeric_env_vars)

    for call in env_var_requests:
        body = json.loads(call.request.body.decode('utf-8'))
        param = json.loads(body['runtimeParameterValues'])[0]
        if param['fieldName'] in string_env_vars:
            assert param['type'] == 'string'
            assert param['value'] == string_env_vars[param['fieldName']]
        elif param['fieldName'] in numeric_env_vars:
            assert param['type'] == 'numeric'
            assert float(param['value']) == float(numeric_env_vars[param['fieldName']])
        else:
            pytest.fail(f"Unexpected environment variable: {param['fieldName']}")


@pytest.mark.usefixtures('api_endpoint_env', 'api_token_env')
@pytest.mark.parametrize(
    'cli_parameters, expected_message',
    (
        (
            ['--image', 'image', '--base-env', 'SomeEnv', '--path', 'project', 'app_name'],
            'Docker container (image) should not be used '
            'with execution environment (base-env) or project folder (path).',
        ),
        (
            ['--image', 'image', '--path', 'project', 'app_name'],
            'Docker container (image) should not be used '
            'with execution environment (base-env) or project folder (path).',
        ),
        (
            ['--image', 'image', '--base-env', 'SomeEnv', 'app_name'],
            'Docker container (image) should not be used '
            'with execution environment (base-env) or project folder (path).',
        ),
        (
            ['--path', 'project', 'app_name'],
            'Execution environment (base-env) and project folder (path) '
            'are both required for creating custom application.',
        ),
        (
            ['--base-env', 'SomeEnv', 'app_name'],
            'Execution environment (base-env) and project folder (path) '
            'are both required for creating custom application.',
        ),
        (
            ['app_name'],
            'Docker container (image) or execution environment (base-env) and '
            'project folder (path) are required for creating custom application.',
        ),
    ),
    ids=('image-env-path', 'image-env', 'image-path', 'only-path', 'only-env', 'no-sources'),
)
def test_create_with_wrong_set_of_params(cli_parameters, expected_message):
    runner = CliRunner()
    with runner.isolated_filesystem():
        # creating folder and file to not trigger image and path existence check
        Path('project').mkdir()
        Path('image').touch()

        result = runner.invoke(create, cli_parameters)

    assert result.exit_code == 2, result.exception
    assert expected_message in result.output


@responses.activate
@pytest.mark.usefixtures('api_token_env')
def test_create_with_name_in_use(api_endpoint_env):
    app_name = 'new_app'

    name_matcher = matchers.query_param_matcher({'name': app_name})
    responses.get(
        f'{api_endpoint_env}/customApplications/nameCheck/',
        json={'inUse': True},
        match=[name_matcher],
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        # creating folder and file to not trigger image existence check
        Path('image').touch()

        result = runner.invoke(create, ['--image', 'image', app_name])

    assert result.exit_code == 2, result.exception
    assert f'Name {app_name} is used by other custom application' in result.output
