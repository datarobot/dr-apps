#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
import posixpath
from typing import Any, Dict, List, Optional, Union

from requests import Session
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from .exceptions import ClientResponseError
from .handle_dr_response import handle_dr_response

IMAGE_BUILD_SUCCESS_STATUSES = {'success'}
IMAGE_BUILD_FAILED_STATUSES = {'failed'}
IMAGE_BUILD_FINAL_STATUSES = IMAGE_BUILD_SUCCESS_STATUSES | IMAGE_BUILD_FAILED_STATUSES


def create_execution_environment(
    session: Session, endpoint: str, env_name: str, description: Optional[str] = None
) -> Dict[str, Any]:
    """Create execution environments that can be used by custom application."""
    url = posixpath.join(endpoint, 'executionEnvironments/')
    payload = {'name': env_name, 'useCases': ['customApplication']}
    if description:
        payload['description'] = description
    response = session.post(url, json=payload)
    handle_dr_response(response)
    return response.json()


def get_execution_environments_list(
    session: Session, endpoint: str, env_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get a list of execution environments with possibility to filter by name."""
    url = posixpath.join(endpoint, 'executionEnvironments/')
    req_params = {'useCases': 'customApplication'}
    if env_name:
        req_params['searchFor'] = env_name

    response = session.get(url, params=req_params)
    handle_dr_response(response)

    env_list = response.json()['data']
    if env_name:
        env_list = [ee for ee in env_list if ee['name'] == env_name]

    return env_list


def get_execution_environment_by_id(
    session: Session, endpoint: str, base_env_id: str
) -> Dict[str, Any]:
    """Get a execution environment by ID."""
    url = posixpath.join(endpoint, f"executionEnvironments/{base_env_id}/")
    response = session.get(url)
    handle_dr_response(response)
    return response.json()


def get_execution_environment_by_name(
    session: Session, endpoint: str, base_env_name: str
) -> Dict[str, Any]:
    """Get an execution environment by name."""
    envs = get_execution_environments_list(session, endpoint, env_name=base_env_name)
    if not envs:
        # imitating that environment is not found
        error_url = posixpath.join(endpoint, 'executionEnvironments/')
        raise ClientResponseError(
            status=404, message='Can\'t find execution environment by name.', url=error_url
        )
    return envs[0]


def create_execution_environment_version(
    session: Session,
    endpoint: str,
    base_env_id: str,
    multipart_data: Union[MultipartEncoder, MultipartEncoderMonitor],
) -> Dict[str, Any]:
    """Create a new execution environment from prebuild image."""
    url = posixpath.join(endpoint, f'executionEnvironments/{base_env_id}/versions/')
    response = session.post(
        url, data=multipart_data, headers={'Content-Type': multipart_data.content_type}
    )
    handle_dr_response(response)
    return response.json()


def get_execution_environment_version_by_id(
    session: Session, endpoint: str, base_env_id: str, version_id: str
) -> Dict[str, Any]:
    """Get a execution environment version by environment ID and version ID."""
    url = posixpath.join(endpoint, f"executionEnvironments/{base_env_id}/versions/{version_id}/")
    response = session.get(url)
    handle_dr_response(response)
    return response.json()
