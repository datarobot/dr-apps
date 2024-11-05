import logging

import pytest
import responses
from bson import ObjectId
from click.testing import CliRunner
from responses import matchers

from drapps.externalshare import external_share

logger = logging.getLogger()


@pytest.mark.parametrize('app_id', [str(ObjectId())])
@responses.activate
@pytest.mark.parametrize('use_name', [True, False])
@pytest.mark.parametrize('allow_external_sharing', [True, False])
@pytest.mark.parametrize('users_to_add', [['new.user.1@datarobot.com', 'new.user.2@datarobot.com']])
@pytest.mark.parametrize('users_to_remove', ['@some-external-domain.com'])
def test_set_external_sharing(
    api_token_env,
    api_endpoint_env,
    app_id,
    allow_external_sharing,
    use_name,
    users_to_add,
    users_to_remove,
):
    """
    Tests two core functionalities of external sharing:
    1. Managing whether it is enabled
    2. Managing external sharing users

    The external sharing API takes in the external sharing list (externalAccessRecipients) as one entity.
    So if you want to add a user to the external sharing list, and you already have 100 users
    you'll need to send the "new" list with the 100 old users and the 1 new user.

    In this CLI I want to make this easier to work with, so instead of having the user supply
    the whole list - which would be unpleasant to scale to 100+ users :) they just supply the changes.
    In this case, we query DataRobot for the current list of users, and just make the changes.
    """
    app = {
        'id': app_id,
        'name': "My Externally Shared App",
        'externalAccessRecipients': [
            'existing.user.1@datarobot.com',
            'existing.user.2@datarobot.com',
            '@some-external-domain.com',
        ],
    }
    expected_external_access_recipients = set(app['externalAccessRecipients'])
    expected_external_access_recipients.update(users_to_add)
    expected_external_access_recipients.remove(users_to_remove)
    auth_matcher = matchers.header_matcher({'Authorization': f'Bearer {api_token_env}'})
    responses.patch(
        f'{api_endpoint_env}/customApplications/{app_id}/',
        json={
            'externalAccessEnabled': allow_external_sharing,
            'externalAccessRecipients': list(expected_external_access_recipients),
        },
        match=[auth_matcher],
    )
    if use_name:
        app_list_url = f'{api_endpoint_env}/customApplications/'
        # check that name filter was used
        params_matcher = matchers.query_param_matcher({'name': app['name']})
        responses.get(
            app_list_url,
            json={'count': 1, 'data': [app]},
            match=[auth_matcher, params_matcher],
        )
    else:
        responses.get(
            f'{api_endpoint_env}/customApplications/{app_id}/',
            json=app,
            match=[auth_matcher],
        )

    # NOTE: If you do cli_args = [app_id, '--set-external-sharing', allow_external_sharing']
    # You get a strange dictionary error for the `True` case.
    cli_args = [
        app['name'] if use_name else app_id,
        '--set-external-sharing',
        allow_external_sharing,
    ]
    for user in users_to_add:
        cli_args.extend(['--add-external-user', user])
    for user in users_to_remove:
        cli_args.extend(['--remove-external-user', user])
    runner = CliRunner()
    result = runner.invoke(external_share, args=cli_args)
    if result.exit_code:
        logger.error(result.output)
    else:
        logger.info(result.output)
    assert result.exit_code == 0, result.exception
