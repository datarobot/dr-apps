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


def get_execution_environments_list(
    session: Session, endpoint: str, env_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get a list of execution environments with possibility to filter by name"""
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
