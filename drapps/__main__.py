#!/usr/bin/env python
#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
from click import Group

from drapps.create import create
from drapps.env import create_env
from drapps.externalshare import external_share
from drapps.logs import logs
from drapps.ls import ls
from drapps.publish import publish, revert_publish
from drapps.terminate import terminate

help_text = (
    'CLI tools for custom applications.\n\n'
    'You can use drapps COMMAND --help for getting more info about command.'
)
drapps = Group(
    commands=[create, ls, logs, terminate, create_env, publish, revert_publish, external_share],
    help=help_text,
)

if __name__ == "__main__":
    drapps()
