#
#  Copyright 2023 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
import io
import os
from pathlib import Path
from typing import BinaryIO, List, Tuple, Union

from click import UsageError

ENTRYPOINT_SCRIPT_NAME = 'start-app.sh'


def file_reader_fix_new_lines(file_path: Path) -> io.BytesIO:
    """Convert Win new lines into *nix new lines."""
    with open(file_path, 'rb') as f:
        content = f.read()
    return io.BytesIO(content.replace(b'\r\n', b'\n'))


def check_project(file_folder: Path):
    """Validate project folder content."""
    # check that entry point script is presented
    entry_point = next(file_folder.glob(ENTRYPOINT_SCRIPT_NAME), None)
    if not entry_point:
        raise UsageError(
            f'You need to have entrypoint script ({ENTRYPOINT_SCRIPT_NAME}) '
            'as part of your project.'
        )
    # check that start-app.sh has correct signature
    with open(entry_point, 'r') as f:
        data = f.read(3)
        if data != '#!/':
            raise UsageError(
                'Please, use correct script signature in entrypoint script '
                f'({ENTRYPOINT_SCRIPT_NAME}). Eg: `#!/usr/bin/env bash`'
            )


def get_project_files_list(file_folder: Path) -> List[Tuple[Path, str]]:
    """Get list of absolute and relative paths for each file in project folder."""
    files_in_folder = [file for file in file_folder.rglob("*") if file.is_file()]
    result = []
    for file in files_in_folder:
        relative_path = str(file.relative_to(file_folder))
        if os.path.sep == '\\':
            # if we work on Windows, convert relative path to UNIX way
            relative_path = relative_path.replace('\\', '/')

        result.append((file, relative_path))
    return result


def get_io_stream(file_path: Path) -> Union[io.BytesIO, BinaryIO]:
    if file_path.name == ENTRYPOINT_SCRIPT_NAME and os.path.sep == '\\':
        # fixing new lines in Windows edited entrypoint file
        return file_reader_fix_new_lines(file_path)

    return file_path.open(mode='rb')
