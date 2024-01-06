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

from .handle_dr_response import handle_dr_response


def get_custom_apps_list(
    session: Session, endpoint: str, app_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get a list of custom application with possibility to filter by application name"""
    url = posixpath.join(endpoint, 'customApplications/')
    req_params = {}
    if app_name:
        req_params['name'] = app_name

    response = session.get(url, params=req_params)
    handle_dr_response(response)
    return response.json()['data']


def get_custom_app_by_id(session: Session, endpoint: str, app_id: str) -> Dict[str, Any]:
    """Get a custom application by ID"""
    url = posixpath.join(endpoint, f'customApplications/{app_id}/')
    response = session.get(url)
    handle_dr_response(response)
    return response.json()


def get_custom_app_logs(session: Session, endpoint: str, app_id: str) -> str:
    """Get runtime logs for a custom application"""
    url = posixpath.join(endpoint, f'customApplications/{app_id}/logs/')
    response = session.get(url)
    handle_dr_response(response)
    records = response.json()['logs']
    return '\n'.join(records)
