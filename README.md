# Custom apps hosting in DataRobot with DRApps

DRApps is a simple command line interface (CLI) providing the tools required to
host a custom application, such as a Streamlit app, in DataRobot using a DataRobot
execution environment. This allows you to run apps without building your own docker
image. Custom applications don't provide any storage; however, you can access the
full DataRobot API and other services.

## Install the DRApps CLI tool

### For users

```sh
pip install git+https://github.com/datarobot/dr-apps
```

### For contributors

To install the DRApps CLI tool, clone this
repository and then install the package by running the following command:

```sh
# If your environment does not already have `build` then run `pip install build` first
python -m build
```

## For Windows Users

For Windows users, you may need to interface with the DR Custom Apps CLI via module calls:

```sh
python -m drapps <your_commands_here>
```

If you have issues entering words with spaces ( eg: `-e "[DataRobot] Python 3.12 Applications Base"` )
then you may find that using ids is a little easier.

## Use the DRApps CLI

After you install the DRApps CLI tool, you can use the `--help` command to
access the following information:

```sh
$ drapps --help
Usage: drapps [OPTIONS] COMMAND [ARGS]...

  CLI tools for custom applications.

  You can use drapps COMMAND --help for getting more info about command.

Options:
  --help  Show this message and exit.

Commands:
  create     Creates new custom application from docker image or base...
  logs       Provides logs for custom application.
  ls         Provides list of custom applications or execution environments.
  terminate  Stops custom application and removes it from the list.
```

You can use `--help` for each command separately for each command

### Create custom application

```sh
$ drapps create --help
Usage: drapps create [OPTIONS] APPLICATION_NAME

  Creates new custom application from docker image or base environment.

  If application created from project folder, custom application image will be
  created or existing will be updated.

Options:
  -t, --token TEXT          Pubic API access token. You can use
                            DATAROBOT_API_TOKEN env instead.
  -E, --endpoint TEXT       Data Robot Public API endpoint. You can use
                            DATAROBOT_ENDPOINT instead. Default:
                            https://app.datarobot.com/api/v2
  -e, --base-env TEXT       Name or ID for execution environment.
  -p, --path DIRECTORY      Path to folder with files that should be uploaded.
  -i, --image FILE          Path to tar archive with custom application docker
                            images.
  --stringEnvVar KEY=VALUE  An environment variable of string type to be passed
                            to the application.
  --numericEnvVar KEY=VALUE An environment variable of integer or float type to
                            be passed to the application.
  --skip-wait               Do not wait for ready status.
  --help                    Show this message and exit.
```

More detailed descriptions for each argument are provided in the table below:

| Argument           | Description                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `APPLICATION_NAME` | Enter the name of your custom application. This name is also used to generate the name of the custom application image, adding `Image` suffix.                                                                                                                                                                                                                                                                                                            |
| `--token`          | Enter your API Key, found on the [**Developer Tools**](https://app.datarobot.com/account/developer-tools) page of your DataRobot account. <br> You can also provide your API Key using the `DATAROBOT_API_TOKEN` environment variable.                                                                                                                                                                                                                    |
| `--endpoint`       | Enter the URL for the DataRobot Public API. The default value is `https://app.datarobot.com/api/v2`. <br> You can also provide the URL to Public API using the `DATAROBOT_ENDPOINT` environment variable.                                                                                                                                                                                                                                                 |
| `--base-env`       | Enter the UUID or name of execution environment used as base for your Streamlit app. The execution environment contains the libraries and packages required by your application. You can find list of available environments in the **Custom Model Workshop** on the [**Environments**](https://app.datarobot.com/model-registry/custom-environments) page. <br> For a custom Streamlit application, use `--base-env '[DataRobot] Python 3.9 Streamlit'`. |
| `--path`           | Enter the path to a folder used to create the custom application. Files from this folder are uploaded to DataRobot and used to create the custom application image. The custom application is started from this image. <br> To use the current working directory, use `--path .`.                                                                                                                                                                         |
| `--stringEnvVar`   | Enter a string key value par like `ENV_VAR_KEY="A string value"` to pass down to the application. It can be referenced in the application code as `MLOPS_RUNTIME_PARAM_{ENV_VAR_KEY}`                                                                                                                                                                                                                                                                     |
| `--numericEnvVar`  | Enter a numeric (integer or float) key value par like `ENV_VAR_KEY=42` or `ENV_VAR_KEY=12.51` to pass down to the application. It can be referenced in the application code as `MLOPS_RUNTIME_PARAM_{ENV_VAR_KEY}`                                                                                                                                                                                                                                        |
| `--image`          | Enter the path to a archive with docker image. <br> You can save your docker image to file with `docker save <image_name> > <file_name>.tar`                                                                                                                                                                                                                                                                                                              |
| `--skip-wait`      | Do not wait till application will finish setup and exit from the scipt directly after application creation request will be send.                                                                                                                                                                                                                                                                                                                          |

### Logs

```sh
$ drapps logs --help
Usage: drapps logs [OPTIONS] APPLICATION_ID_OR_NAME

  Provides logs for custom application.

Options:
  -t, --token TEXT     Pubic API access token. You can use DATAROBOT_API_TOKEN
                       env instead.
  -E, --endpoint TEXT  Data Robot Public API endpoint. You can use
                       DATAROBOT_ENDPOINT instead. Default:
                       https://app.datarobot.com/api/v2
  -f, --follow         Output append data as new log records appear.
  --help               Show this message and exit.
```

| Argument                 | Description                                                                                                                                                                                                                            |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `APPLICATION_ID_OR_NAME` | ID or name of application, which logs you want to see.                                                                                                                                                                                 |
| `--token`                | Enter your API Key, found on the [**Developer Tools**](https://app.datarobot.com/account/developer-tools) page of your DataRobot account. <br> You can also provide your API Key using the `DATAROBOT_API_TOKEN` environment variable. |
| `--endpoint`             | Enter the URL for the DataRobot Public API. The default value is `https://app.datarobot.com/api/v2`. <br> You can also provide the URL to Public API using the `DATAROBOT_ENDPOINT` environment variable.                              |
| `--follow`               | Script continues checking for new log records and displays if they appear                                                                                                                                                              |

### List of base custom applications or base environments

```sh
$ drapps ls --help
Usage: drapps ls [OPTIONS] {apps|envs}

  Provides list of custom applications or execution environments.

Options:
  -t, --token TEXT     Pubic API access token. You can use DATAROBOT_API_TOKEN
                       env instead.
  -E, --endpoint TEXT  Data Robot Public API endpoint. You can use
                       DATAROBOT_ENDPOINT instead. Default:
                       https://app.datarobot.com/api/v2
  --id-only            Output only ids
  --help               Show this message and exit.
```

| Argument     | Description                                                                                                                                                                                                                            |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--token`    | Enter your API Key, found on the [**Developer Tools**](https://app.datarobot.com/account/developer-tools) page of your DataRobot account. <br> You can also provide your API Key using the `DATAROBOT_API_TOKEN` environment variable. |
| `--endpoint` | Enter the URL for the DataRobot Public API. The default value is `https://app.datarobot.com/api/v2`. <br> You can also provide the URL to Public API using the `DATAROBOT_ENDPOINT` environment variable.                              |
| `--id-only`  | Show only IDs of entity. <br> Can be useful with piping to terminate command                                                                                                                                                           |

### Terminate

```sh
$ drapps terminate --help
Usage: drapps terminate [OPTIONS] APPLICATION_ID_OR_NAME...

  Stops custom application and removes it from the list.

Options:
  -t, --token TEXT     Pubic API access token. You can use DATAROBOT_API_TOKEN
                       env instead.
  -E, --endpoint TEXT  Data Robot Public API endpoint. You can use
                       DATAROBOT_ENDPOINT instead. Default:
                       https://app.datarobot.com/api/v2
  --help               Show this message and exit.
```

| Argument                 | Description                                                                                                                                                                                                                            |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `APPLICATION_ID_OR_NAME` | Space separated list of IDs or names of applications, that needs to be removed.                                                                                                                                                        |
| `--token`                | Enter your API Key, found on the [**Developer Tools**](https://app.datarobot.com/account/developer-tools) page of your DataRobot account. <br> You can also provide your API Key using the `DATAROBOT_API_TOKEN` environment variable. |
| `--endpoint`             | Enter the URL for the DataRobot Public API. The default value is `https://app.datarobot.com/api/v2`. <br> You can also provide the URL to Public API using the `DATAROBOT_ENDPOINT` environment variable.                              |

### Create a new Execution Environment

It may be the case that your version of DataRobot (eg Single Tenant SAAS or On-Prem) was not shipped with the `[DataRobot] Python 3.12 Applications Base`
or that you want to make a new execution environment for your apps (eg you want to make a Flask app, or you want your base docker image
to have some packages installed in it that don't come standard

First you will need to make a dockerfile. For the default `[DataRobot] Python 3.12 Applications Base` env we use:

```dockerfile
FROM python:3.12-slim

# This makes print statements show up in the logs API
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/code

EXPOSE 8080
```

That dockerfile will then need to be archived into a zip file. For this example we named the zip file `dockerfile.zip`.
Once you have the file zipped, and you open a terminal in the directory you can use the apps CLI:

```
drapps create-env --dockerfilezip dockerfile.zip --name "[DataRobot] Python 3.12 Applications Base"
```

## Deploy an example app

To test this, deploy an example Streamlit app using the following command from
the root directory of this repo:

```sh
drapps create -t <your_api_token> -e "[DataRobot] Python 3.12 Applications Base" -p ./demo-streamlit DemoApp
```

This example script works as follows:

1. Finds the execution environment through the `/api/v2/executionEnvironments/`
   endpoint by the name or UUID you provided, verifying if the environment can be
   used for the custom application and retrieving the ID of the latest environment version.

2. Finds or creates the custom application image through the `/api/v2/customApplicationImages/`
   endpoint, named by adding the `Image` suffix to the provided application name (i.e., `CustomApp Image`).

3. Creates a new version of a custom application image through the `customApplicationImages/<appImageId>/versions`
   endpoint, uploading all files from the directory you provided and setting the execution
   environment version defined in the first step.

4. Starts a new application with the custom application image version created
   in the previous step.

When this script runs successfully, link to it appears
in the terminal. Also, you can access the application on the DataRobot
Applications tab [Non EU DataRobot](https://app.datarobot.com/applications) [EU DataRobot](https://app.eu.datarobot.com/applications).

> [!IMPORTANT]
> To access the application, you must be logged into the DataRobot instance and
> account associated with the application.

## Considerations

Consider the following when creating a custom app:

- The root directory of the custom application must contain a `start-app.sh` file,
  used as the entry point for starting your application server.

- The web server of the application must listen on port `8080`.

- The required packages must be listed in a `requirements.txt` file in the application's
  root directory for automatic installation during application setup.

- The application should authenticate with the DataRobot API through the `DATAROBOT_API_TOKEN` environment variable with a key found under `Developer Tools` on the DataRobot UI. The DataRobot package on PyPi already authenticates this way. This environment variable will automatically be added to your running container by the custom apps service.

- The application should access the DataRobot Public API URL for the current environment through the `DATAROBOT_ENDPOINT` environment variable. The DataRobot package on PyPi already uses this route. This environment variable will automatically be added to your running container by the custom apps service
