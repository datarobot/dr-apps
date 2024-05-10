#
#  Copyright 2024 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#  Released under the terms of DataRobot Tool and Utility Agreement.
#
from itertools import islice, repeat
from pathlib import Path
from time import sleep
from typing import Any, Dict, Iterator, List, Optional, Tuple

import click
from bson import ObjectId
from click._termui_impl import ProgressBar
from requests import Session
from requests_toolbelt import MultipartEncoderMonitor

from .helpers.app_projects_functions import check_project, get_io_stream, get_project_files_list
from .helpers.custom_app_sources_functions import (
    create_application_source_version,
    create_custom_app_source,
    get_custom_app_source_by_name,
    get_custom_app_source_versions_list,
    update_application_source_version,
)
from .helpers.custom_apps_functions import (
    FINAL_STATUSES,
    SUCCESS_STATUSES,
    check_starting_status,
    create_custom_app,
    get_custom_app_logs,
    is_app_name_in_use,
)
from .helpers.exceptions import ClientResponseError
from .helpers.execution_environments_functions import (
    IMAGE_BUILD_FAILED_STATUSES,
    IMAGE_BUILD_FINAL_STATUSES,
    create_execution_environment,
    create_execution_environment_version,
    get_execution_environment_by_id,
    get_execution_environment_by_name,
    get_execution_environment_version_by_id,
)
from .helpers.wrappers import api_endpoint, api_token

UPLOAD_CHUNK_SIZE = 50
CHECK_STATUS_WAIT_TIME = 5


def validate_parameters(
    base_env: Optional[str], path: Optional[Path], image: Optional[Path]
) -> None:
    message = None
    if not (base_env or path or image):
        message = (
            'Docker container (image) or execution environment (base-env) and '
            'project folder (path) are required for creating custom application.'
        )
    elif image and (base_env or path):
        message = (
            'Docker container (image) should not be used with execution environment '
            '(base-env) or project folder (path).'
        )
    elif bool(base_env) != bool(path):
        message = (
            'Execution environment (base-env) and project folder (path) are '
            'both required for creating custom application.'
        )

    if message:
        raise click.UsageError(message)


def get_base_env_version(session: Session, endpoint: str, base_env: str) -> str:
    try:
        if ObjectId.is_valid(base_env):
            env = get_execution_environment_by_id(session, endpoint, base_env)
        else:
            env = get_execution_environment_by_name(session, endpoint, base_env)
    except ClientResponseError as error:
        if error.status != 404:
            raise error
        message = f"Can't find {base_env} that can be used for creating custom application"
        raise click.BadParameter(message, param_hint='--base-env')

    if not env.get('latestVersion'):
        message = f"Can't find last version for environment {base_env}."
        raise click.BadParameter(message, param_hint='--base-env')

    return env['latestVersion']['id']


def create_new_custom_app_source_version(
    session: Session, endpoint: str, source_name: str
) -> Tuple[str, str]:
    try:
        app_source = get_custom_app_source_by_name(session, endpoint, source_name)
        versions = get_custom_app_source_versions_list(session, endpoint, app_source['id'])
        version_count = len(versions)
    except ClientResponseError as error:
        if error.status != 404:
            raise error
        # create a new app source if we can't find existing
        app_source = create_custom_app_source(session, endpoint, source_name)
        version_count = 0

    click.echo(f'Using {source_name} custom application source.')
    version_label = f'script_generated_{version_count}'
    new_version = create_application_source_version(
        session, endpoint, app_source['id'], version_label
    )
    click.echo(f'Creating new version for {source_name} custom application source.')
    return app_source['id'], new_version['id']


def split_list_into_chunks(iterable: List[Any], chunk_size: int) -> Iterator[Tuple[Any, ...]]:
    """Generator that splits a list into chunks of specified size."""
    iterator = iter(iterable)
    return iter(lambda: tuple(islice(iterator, chunk_size)), ())


def configure_custom_app_source_version(
    session: Session,
    endpoint: str,
    custom_app_source_id: str,
    custom_app_source_version_id: str,
    project: Path,
    base_env_version_id: str,
) -> None:
    payload: Dict[str, Any] = {'baseEnvironmentVersionId': base_env_version_id}
    project_files = get_project_files_list(project)

    progress: ProgressBar  # type hinting badly needed by mypy
    with click.progressbar(length=len(project_files), label='Uploading project:') as progress:
        # grouping project files in chunks
        for file_chunk in split_list_into_chunks(project_files, chunk_size=UPLOAD_CHUNK_SIZE):
            files_streams = [get_io_stream(file_tuple[0]) for file_tuple in file_chunk]
            files_relative_paths = [file_tuple[1] for file_tuple in file_chunk]

            payload['filePath'] = files_relative_paths
            payload['file'] = files_streams

            update_application_source_version(
                session, endpoint, custom_app_source_id, custom_app_source_version_id, payload
            )
            # closing all streams after upload
            for files_stream in files_streams:
                if not files_stream.closed:
                    files_stream.close()

            payload = {}
            progress.update(len(file_chunk))


def create_app_from_project(
    session: Session, endpoint: str, base_env: str, project_folder: Path, app_name: str
) -> Dict[str, Any]:
    base_env_version_id = get_base_env_version(session, endpoint, base_env)
    source_name = f'{app_name}Source'
    custom_app_source_id, custom_app_source_version_id = create_new_custom_app_source_version(
        session, endpoint, source_name
    )
    configure_custom_app_source_version(
        session=session,
        endpoint=endpoint,
        custom_app_source_id=custom_app_source_id,
        custom_app_source_version_id=custom_app_source_version_id,
        project=project_folder,
        base_env_version_id=base_env_version_id,
    )
    app_payload = {'name': app_name, 'applicationSourceId': custom_app_source_id}
    click.echo(f'Starting {app_name} custom application.')
    return create_custom_app(session, endpoint, app_payload)


def wait_for_execution_environment_version_ready(
    session: Session, endpoint: str, base_env_id: str, version_id: str
) -> None:
    with click.progressbar(iterable=repeat(0), label='Waiting till image is ready:') as progress:
        while True:
            response = get_execution_environment_version_by_id(
                session=session, endpoint=endpoint, base_env_id=base_env_id, version_id=version_id
            )
            img_status = response.get('buildStatus')
            if img_status in IMAGE_BUILD_FINAL_STATUSES:
                break
            progress.update(1)
            sleep(CHECK_STATUS_WAIT_TIME)
    if img_status in IMAGE_BUILD_FAILED_STATUSES:
        raise Exception("Image build failed")


def send_docker_image_with_progress(
    session: Session, endpoint: str, base_env_id: str, docker_image: Path
) -> None:
    click.echo(f'Uploading {docker_image.name} to Data Robot.')
    with docker_image.open('rb') as file:
        multipart_monitor = MultipartEncoderMonitor.from_fields(
            fields={'docker_image': (docker_image.name, file, 'application/octet-stream')}
        )
        progress: ProgressBar  # type hinting badly needed by mypy
        with click.progressbar(length=multipart_monitor.len, label='Upload progress:') as progress:

            def monitor_callback(monitor: MultipartEncoderMonitor):
                bytes_send = monitor.bytes_read - progress.pos
                progress.update(bytes_send)

            multipart_monitor.callback = monitor_callback

            response = create_execution_environment_version(
                session=session,
                endpoint=endpoint,
                base_env_id=base_env_id,
                multipart_data=multipart_monitor,
            )
    wait_for_execution_environment_version_ready(
        session=session, endpoint=endpoint, base_env_id=base_env_id, version_id=response['id']
    )


def create_app_from_docker_image(
    session: Session, endpoint: str, docker_image: Path, app_name: str
) -> Dict[str, Any]:
    base_env_data = create_execution_environment(
        session=session,
        endpoint=endpoint,
        env_name=docker_image.name,
        description='Environment for prebuild image with a custom application.',
    )

    send_docker_image_with_progress(
        session=session,
        endpoint=endpoint,
        base_env_id=base_env_data['id'],
        docker_image=docker_image,
    )

    app_payload = {'name': app_name, 'environmentId': base_env_data['id']}
    click.echo(f'Starting {app_name} custom application.')
    return create_custom_app(session, endpoint, app_payload)


def wait_for_custom_app_spinning(session: Session, status_check_url: str) -> str:
    with click.progressbar(iterable=repeat(0), label='Waiting till app is ready:') as progress:
        while True:
            app_status = check_starting_status(session, status_check_url)
            if app_status in FINAL_STATUSES:
                return app_status
            progress.update(1)
            sleep(CHECK_STATUS_WAIT_TIME)


@click.command()
@api_token
@api_endpoint
@click.option(
    '-e',
    '--base-env',
    required=False,
    type=click.STRING,
    help='Name or ID for execution environment.',
)
@click.option(
    '-p',
    '--path',
    required=False,
    type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path),
    help='Path to folder with files that should be uploaded.',
)
@click.option(
    '-i',
    '--image',
    required=False,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    help='Path to tar archive with custom application docker images.',
)
@click.option(
    '--skip-wait',
    is_flag=True,
    show_default=True,
    default=False,
    help='Do not wait for ready status.',
)
@click.argument('application_name', type=click.STRING, required=True)
def create(
    token: str,
    endpoint: str,
    base_env: Optional[str],
    path: Optional[Path],
    image: Optional[Path],
    skip_wait: bool,
    application_name: str,
) -> None:
    """
    Creates new custom application from docker image or base environment.

    If application created from project folder, custom application image will be created
    or existing will be updated.
    """
    validate_parameters(base_env, path, image)
    if path:
        check_project(path)

    session = Session()
    session.headers.update({'Authorization': f'Bearer {token}'})

    if is_app_name_in_use(session, endpoint, application_name):
        message = f'Name {application_name} is used by other custom application'
        raise click.BadParameter(message, param_hint='APPLICATION_NAME')

    if image:
        app_data = create_app_from_docker_image(
            session=session, endpoint=endpoint, docker_image=image, app_name=application_name
        )
    else:
        app_data = create_app_from_project(
            session=session,
            endpoint=endpoint,
            base_env=base_env,  # type: ignore[arg-type]
            project_folder=path,  # type: ignore[arg-type]
            app_name=application_name,
        )

    if skip_wait or not app_data.get('statusUrl'):
        click.echo(f'Custom application {application_name} was successfully created.')
        return

    final_status = wait_for_custom_app_spinning(
        session=session, status_check_url=app_data['statusUrl']
    )

    if final_status in SUCCESS_STATUSES:
        click.echo(f'Custom application is running: {app_data["applicationUrl"]}')
        return

    click.echo('Custom application did not achieve stable state.', err=True)
    logs = get_custom_app_logs(session=session, endpoint=endpoint, app_id=app_data['id'])

    dependency_build_error = logs.get('buildError')
    runtime_log = '\n'.join(logs.get('logs', []))

    if dependency_build_error:
        click.echo(
            f'Error happened during dependency image build: {dependency_build_error}', err=True
        )
        dependency_build_logs = logs.get('buildLog')
        if dependency_build_logs:
            click.echo(dependency_build_logs, err=True)

    elif runtime_log:
        click.echo('Runtime log:', err=True)
        click.echo(runtime_log, err=True)

    else:
        click.echo(
            f'There are no logs for application {app_data["id"]}. Please get in touch with support.',
            err=True,
        )
