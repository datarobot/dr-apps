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

from drapps.publish import publish, revert_publish


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


@responses.activate
@pytest.mark.parametrize('use_name_for_src_app', [False, True])
def test_revert_publish_by_index(api_token_env, api_endpoint_env, use_name_for_src_app):
    """
    Most likely case is a user wants to revert to the last published app.
    This is supposed to sorta rhyme with git's
    "git reset --hard HEAD~1"
    but instead be:
    "drapps revert-publish -i MyApp --by=1"
    which should be familiar to a lot of developers.
    Potentially in the future, we could have a `soft` revert which makes a new app?
    """
    auth_matcher = matchers.header_matcher({'Authorization': f'Bearer {api_token_env}'})
    app_name = "Custom Publishing App"
    app_id = ObjectId('669fdb684d44ac1c99dda99c')
    index = 3
    if use_name_for_src_app:
        app_list_url = f'{api_endpoint_env}/customApplications/'
        # check that name filter was used
        params_matcher = matchers.query_param_matcher({'name': app_name})
        responses.get(
            app_list_url,
            json={'count': 1, 'data': [{'id': str(app_id), 'name': app_name}]},
            match=[auth_matcher, params_matcher],
        )

    cli_args = ['-i', app_name if use_name_for_src_app else app_id]
    # Since we know the index, we can query with pagination to read the history.
    history_params_matcher = matchers.query_param_matcher({'limit': 1, 'offset': index - 1})
    # There are more attrs on the object, but they aren't used here
    history_entity = {'sourceVersionId': str(ObjectId())}
    responses.get(
        f'{api_endpoint_env}/customApplications/{app_id}/history/',
        json={'count': 1, 'data': [history_entity]},
        match=[auth_matcher, history_params_matcher],
    )

    # We then want to verify that the publish API is called with the proper
    responses.patch(
        f'{api_endpoint_env}/customApplications/{app_id}/',
        json={'customApplicationSourceVersionId': history_entity['sourceVersionId']},
        match=[auth_matcher],
        status=204,
    )

    responses.get(
        f'{api_endpoint_env}/customApplications/{app_id}/',
        json={'status': 'running'},
        match=[auth_matcher],
    )

    runner = CliRunner()
    result = runner.invoke(revert_publish, [*cli_args, '--by', index])

    logger = logging.getLogger()
    if result.exit_code:
        logger.error(result.output)
    else:
        logger.info(result.output)

    assert result.exit_code == 0, result.output
