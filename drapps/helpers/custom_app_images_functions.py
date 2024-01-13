#
#  Copyright 2024 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
import posixpath
from typing import Any, Dict, List

from requests import Session

from .exceptions import ClientResponseError
from .handle_dr_response import handle_dr_response


def create_custom_app_image(session: Session, endpoint: str, name: str) -> Dict[str, Any]:
    """Create new custom application image."""
    url = posixpath.join(endpoint, "customApplicationImages/")
    response = session.post(url, json={"name": name})
    handle_dr_response(response)
    return response.json()


def get_custom_app_images_list(session: Session, endpoint: str) -> List[Dict[str, Any]]:
    """Get a list of custom application images."""
    url = posixpath.join(endpoint, 'customApplicationImages/')
    response = session.get(url)
    handle_dr_response(response)
    return response.json()['data']


def get_custom_app_image_by_id(session: Session, endpoint: str, image_id: str) -> Dict[str, Any]:
    """Get a custom application image by ID."""
    url = posixpath.join(endpoint, f'customApplicationImages/{image_id}/')
    response = session.get(url)
    handle_dr_response(response)
    return response.json()


def get_custom_app_image_by_name(
    session: Session, endpoint: str, image_name: str
) -> Dict[str, Any]:
    """Get a custom application image by name."""
    images = get_custom_app_images_list(session, endpoint)
    for image in images:
        if image['name'] == image_name:
            return image

    # imitating that app is not found
    error_url = posixpath.join(endpoint, 'customApplications/')
    raise ClientResponseError(
        status=404, message='Can\'t find custom application by name.', url=error_url
    )


def create_application_image_version(
    session: Session, endpoint: str, image_id: str, version_label: str
) -> Dict[str, Any]:
    """Create new application image version."""
    url = posixpath.join(endpoint, f"customApplicationImages/{image_id}/versions/")
    response = session.post(url, json={"label": version_label})
    handle_dr_response(response)
    return response.json()


def update_application_image_version(
    session: Session, endpoint: str, image_id: str, version_id: str, payload: Dict[str, Any]
):
    """Make a change to application image version."""
    url = posixpath.join(endpoint, f"customApplicationImages/{image_id}/versions/{version_id}/")
    patch_params: Dict[str, Any] = {'data': payload}
    if 'file' in payload:
        files_data = payload.pop('file')
        files = [("file", file) for file in files_data]
        patch_params['files'] = files

    response = session.patch(url, **patch_params)
    handle_dr_response(response)


def get_custom_app_image_versions_list(
    session: Session, endpoint: str, image_id: str
) -> List[Dict[str, Any]]:
    """Get a list of versions for specific custom application image."""
    url = posixpath.join(endpoint, f'customApplicationImages/{image_id}/versions/')
    response = session.get(url)
    handle_dr_response(response)
    return response.json()['data']
