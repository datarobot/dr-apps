#
#  Copyright 2024 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#


import logging

import pytest
import responses
from bson import ObjectId
from click.testing import CliRunner
from responses import matchers

from drapps.publish import publish


@responses.activate
@pytest.mark.parametrize('app_id', [ObjectId()])
@pytest.mark.parametrize('old_name', ['old name'])
@pytest.mark.parametrize('src_app_id', [ObjectId('6661f524e81dd6bef7fbe9ff')])
@pytest.mark.parametrize(
    'change',
    [
        {'name': 'new name'},
        {'sourceApp': ObjectId('6661f524e81dd6bef7fbe9ff')},
        {'sourceApp': 'src app name'},
    ],
)
@pytest.mark.parametrize('use_name_for_src_app', (False, True))
def test_publish_app(
    old_name, change, use_name_for_src_app, api_token_env, api_endpoint_env, app_id, src_app_id
):
    auth_matcher = matchers.header_matcher({'Authorization': f'Bearer {api_token_env}'})
    new_custom_application_source_version_id = None
    if use_name_for_src_app:
        app_list_url = f'{api_endpoint_env}/customApplications/'
        # check that name filter was used
        params_matcher = matchers.query_param_matcher({'name': old_name})
        responses.get(
            app_list_url,
            json={'count': 1, 'data': [{'id': str(app_id), 'name': old_name}]},
            match=[auth_matcher, params_matcher],
        )
    if change.get('sourceApp'):
        # check that name filter was used
        new_custom_application_source_version_id = ObjectId()
        app_rsp = {
            'id': str(src_app_id),
            'customApplicationSourceVersionId': str(new_custom_application_source_version_id),
        }
        if ObjectId.is_valid(change['sourceApp']):
            responses.get(
                f'{api_endpoint_env}/customApplications/{src_app_id}/',
                json=app_rsp,
                match=[auth_matcher],
            )
        else:
            app_list_url = f'{api_endpoint_env}/customApplications/'
            params_matcher = matchers.query_param_matcher({'name': change['sourceApp']})
            app_rsp['name'] = change['sourceApp']
            responses.get(
                app_list_url,
                json={'count': 1, 'data': [app_rsp]},
                match=[auth_matcher, params_matcher],
            )
    cli_args = ['-i', old_name if use_name_for_src_app else app_id]
    expected_payload = {}
    if 'name' in change:
        expected_payload['name'] = change['name']
        cli_args.extend(['--name', change["name"]])
    if 'sourceApp' in change:
        expected_payload['customApplicationSourceVersionId'] = str(
            new_custom_application_source_version_id
        )
        cli_args.extend(['-s', change["sourceApp"]])

    app_url = f'{api_endpoint_env}/customApplications/{app_id}/'
    responses.patch(
        app_url, status=204, match=[auth_matcher, matchers.json_params_matcher(expected_payload)]
    )

    runner = CliRunner()
    result = runner.invoke(publish, [*cli_args, '--skip-wait'])
    logger = logging.getLogger()
    if result.exit_code:
        logger.error(result.output)
    else:
        logger.info(result.output)
    assert result.exit_code == 0, result.exception
