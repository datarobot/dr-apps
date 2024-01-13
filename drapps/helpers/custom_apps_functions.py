#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
import posixpath
from typing import Any, Dict, List, Optional

from requests import Session

from .exceptions import ClientResponseError
from .handle_dr_response import handle_dr_response

SUCCESS_STATUSES = {'COMPLETED'}
FAILED_STATUSES = {'ERROR', 'ABORTED', 'EXPIRED'}
FINAL_STATUSES = SUCCESS_STATUSES | FAILED_STATUSES


def create_custom_app(session: Session, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create new custom application.
    Payload should include name and applicationImageId or environmentId
    """
    url = posixpath.join(endpoint, 'customApplications/')
    response = session.post(url, json=payload)
    handle_dr_response(response)
    app_data = response.json()
    # adding URL for status checking
    app_data['statusUrl'] = response.headers.get('Location')
    return app_data


def get_custom_apps_list(
    session: Session, endpoint: str, app_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get a list of custom application with possibility to filter by application name."""
    url = posixpath.join(endpoint, 'customApplications/')
    req_params = {}
    if app_name:
        req_params['name'] = app_name

    response = session.get(url, params=req_params)
    handle_dr_response(response)
    return response.json()['data']


def get_custom_app_by_id(session: Session, endpoint: str, app_id: str) -> Dict[str, Any]:
    """Get a custom application by ID."""
    url = posixpath.join(endpoint, f'customApplications/{app_id}/')
    response = session.get(url)
    handle_dr_response(response)
    return response.json()


def get_custom_app_by_name(session: Session, endpoint: str, app_name: str) -> Dict[str, Any]:
    """Get a custom application by name."""
    apps = get_custom_apps_list(session, endpoint, app_name=app_name)
    if not apps:
        # imitating that app is not found
        error_url = posixpath.join(endpoint, 'customApplications/')
        raise ClientResponseError(
            status=404, message='Can\'t find custom application by name.', url=error_url
        )
    return apps[0]


def get_custom_app_logs(session: Session, endpoint: str, app_id: str) -> str:
    """Get runtime logs for a custom application."""
    url = posixpath.join(endpoint, f'customApplications/{app_id}/logs/')
    response = session.get(url)
    handle_dr_response(response)
    records = response.json()['logs']
    return '\n'.join(records)


def delete_custom_app(session: Session, endpoint: str, app_id: str) -> None:
    """Delete custom application."""
    url = posixpath.join(endpoint, f'customApplications/{app_id}/')
    response = session.delete(url)
    handle_dr_response(response)


def is_app_name_in_use(session: Session, endpoint: str, name: str) -> bool:
    """Check if name is already used by other custom application."""
    url = posixpath.join(endpoint, 'customApplications/nameCheck/')
    response = session.get(url, params={'name': name})
    handle_dr_response(response)
    return response.json()['inUse']


def check_starting_status(session: Session, status_url: str) -> str:
    """Use job status API to check if app is ready."""
    response = session.get(status_url, allow_redirects=False)
    handle_dr_response(response)
    # redirection also mean that app was started successfully
    status = 'COMPLETED' if response.status_code == 303 else response.json()['status']
    return status
