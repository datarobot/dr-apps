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
from drapps.logs import logs
from drapps.ls import ls
from drapps.terminate import terminate

help_text = (
    'CLI tools for custom applications.\n\n'
    'You can use drapps COMMAND --help for getting more info about command.'
)
drapps = Group(
    commands=[create, ls, logs, terminate],
    help=help_text,
)

if __name__ == "__main__":
    drapps()
