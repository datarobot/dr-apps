#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
import io
from pathlib import Path


def file_reader_fix_new_lines(file_path: Path) -> io.BytesIO:
    with open(file_path, 'rb') as f:
        content = f.read()
    return io.BytesIO(content.replace(b'\r\n', b'\n'))
