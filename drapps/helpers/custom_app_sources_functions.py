#
#  Copyright 2024 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
import json
import posixpath
from typing import Any, Dict, List, Optional

from requests import Session

from .exceptions import ClientResponseError
from .handle_dr_response import handle_dr_response


def create_custom_app_source(session: Session, endpoint: str, name: str) -> Dict[str, Any]:
    """Create new custom application source."""
    url = posixpath.join(endpoint, "customApplicationSources/")
    response = session.post(url, json={"name": name})
    handle_dr_response(response)
    return response.json()


def get_custom_app_sources_list(session: Session, endpoint: str) -> List[Dict[str, Any]]:
    """Get a list of custom application sources."""
    url = posixpath.join(endpoint, 'customApplicationSources/')
    response = session.get(url)
    handle_dr_response(response)
    return response.json()['data']


def get_custom_app_source_by_id(session: Session, endpoint: str, source_id: str) -> Dict[str, Any]:
    """Get a custom application source by ID."""
    url = posixpath.join(endpoint, f'customApplicationSources/{source_id}/')
    response = session.get(url)
    handle_dr_response(response)
    return response.json()


def get_custom_app_source_by_name(
    session: Session, endpoint: str, source_name: str
) -> Dict[str, Any]:
    """Get a custom application source by name."""
    sources = get_custom_app_sources_list(session, endpoint)
    for source in sources:
        if source['name'] == source_name:
            return source

    # imitating that app is not found
    error_url = posixpath.join(endpoint, 'customApplicationSources/')
    raise ClientResponseError(
        status=404, message='Can\'t find custom application source by name.', url=error_url
    )


def create_application_source_version(
    session: Session, endpoint: str, source_id: str, version_label: str
) -> Dict[str, Any]:
    """Create new application source version."""
    url = posixpath.join(endpoint, f"customApplicationSources/{source_id}/versions/")
    response = session.post(url, json={"label": version_label})
    handle_dr_response(response)
    return response.json()


def update_application_source_version(
    session: Session,
    endpoint: str,
    source_id: str,
    version_id: str,
    payload: Dict[str, Any],
):
    """Make a change to application source version."""
    url = posixpath.join(endpoint, f"customApplicationSources/{source_id}/versions/{version_id}/")
    patch_params: Dict[str, Any] = {'data': payload}
    if 'file' in payload:
        files_data = payload.pop('file')
        files = [("file", file) for file in files_data]
        patch_params['files'] = files
    response = session.patch(url, **patch_params)
    handle_dr_response(response)


def update_runtime_params(
    session: Session,
    endpoint: str,
    source_id: str,
    version_id: str,
    runtime_params: List[str],
):
    url = posixpath.join(endpoint, f"customApplicationSources/{source_id}/versions/{version_id}/")

    for param in runtime_params:
        response = session.patch(url, json={'runtimeParameterValues': param})
        handle_dr_response(response)


def update_resources(
    session: Session,
    endpoint: str,
    source_id: str,
    version_id: str,
    service_requests_on_root_path: bool,
    replicas: Optional[int] = None,
    cpu_size: Optional[str] = None,
    session_affinity: Optional[bool] = None,
):
    resources = dict()
    if replicas is not None:
        resources["replicas"] = replicas
    if cpu_size is not None:
        if cpu_size == '2xsmall':
            cpu_size = 'nano'
        elif cpu_size == 'xsmall':
            cpu_size = 'micro'
        resources["resourceLabel"] = f'cpu.{cpu_size}'  # type: ignore
    if session_affinity is not None:
        resources["sessionAffinity"] = session_affinity
    resources["serviceWebRequestsOnRootPath"] = service_requests_on_root_path
    url = posixpath.join(endpoint, f"customApplicationSources/{source_id}/versions/{version_id}/")
    form_data = {"resources": (None, json.dumps(resources), 'application/json')}
    rsp = session.patch(url, files=form_data)
    handle_dr_response(rsp)


def get_custom_app_source_versions_list(
    session: Session, endpoint: str, source_id: str
) -> List[Dict[str, Any]]:
    """Get a list of versions for specific custom application source."""
    url = posixpath.join(endpoint, f'customApplicationSources/{source_id}/versions/')
    response = session.get(url)
    handle_dr_response(response)
    return response.json()['data']
