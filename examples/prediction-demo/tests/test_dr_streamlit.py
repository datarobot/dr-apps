import pytest
import responses
import json
from bson import ObjectId
from datarobot import TARGET_TYPE
from streamlit.testing.v1 import AppTest

"""
See docs here: https://docs.streamlit.io/develop/api-reference/app-testing
"""


@pytest.fixture
def deploymentid():
    return str(ObjectId())


@pytest.fixture
def projectid():
    return str(ObjectId())


@pytest.fixture
def modelid():
    return str(ObjectId())


@pytest.fixture
def token():
    return f"token-{ObjectId()}-{ObjectId()}"


@pytest.fixture()
def datarobot_prediction_api_key():
    return f"key-{ObjectId()}"


@pytest.fixture
def datarobot_url():
    return "https://testFakeDomain.datarobot.com/api/v2/"


@pytest.fixture
def datarobot_prediction_api_url():
    return "https://fake-prediction-domain.dynamic.orm.datarobot.com"


@pytest.fixture
def setup_standard_env_vars(monkeypatch, deploymentid, projectid, token, datarobot_url):
    monkeypatch.setenv('deploymentid', deploymentid)
    monkeypatch.setenv('projectid', projectid)
    monkeypatch.setenv('token', token)
    monkeypatch.setenv('endpoint', datarobot_url)


@pytest.fixture
def mock_version_api(datarobot_url):
    responses.get(
        f'{datarobot_url}version/',
        json={"major": 2, "minor": 34, "versionString": "2.34.0", "releasedVersion": "2.33.0"}
    )


@pytest.fixture
def mock_deployment_api(
        datarobot_url,
        deploymentid,
        modelid,
        projectid,
        datarobot_prediction_api_key,
        datarobot_prediction_api_url
):
    ps_id = str(ObjectId())
    responses.get(
        f'{datarobot_url}deployments/{deploymentid}/',
        json={
            'id': deploymentid,
            'model': {
                'id': modelid,
                'projectId': projectid,
            },
            'defaultPredictionServer': {
                'id': ps_id,
                "url": datarobot_prediction_api_url,
                "datarobot-key": datarobot_prediction_api_key,
                "suspended": False
            },
            "predictionEnvironment": {
                "id": ps_id,
                "name": datarobot_prediction_api_url,
                "platform": "datarobot",
                "plugin": None,
                "supportedModelFormats": [
                    "datarobot",
                ],
                "isManagedByManagementAgent": False
            },
        },
    )
    responses.get(
        f'{datarobot_url}deployments/{deploymentid}/settings/',
        json={
            "associationId": {
                "columnNames": None,
                "requiredInPredictionRequests": False,
                "autoGenerateId": False,
            },
        },
    )


@pytest.fixture
def positive_class():
    return 1


@pytest.fixture
def mock_project_api(datarobot_url, projectid, positive_class):
    responses.get(
        f'{datarobot_url}projects/{projectid}/',
        json={
            'id': projectid,
            'targetType': TARGET_TYPE.BINARY,
            'positiveClass': positive_class,
        }
    )


@pytest.fixture
def mock_deployment_feature_api(datarobot_url, deploymentid):
    responses.get(
        f'{datarobot_url}deployments/{deploymentid}/features/',
        json={
            "count": 3,
            "next": None,
            "previous": None,
            "data": [
                {
                    "name": "numFeat",
                    "featureType": "Numeric",
                    "importance": 0.1,
                    "dateFormat": None,
                    "knownInAdvance": False
                },
                {
                    "name": "catFeat",
                    "featureType": "Categorical",
                    "importance": 0.2,
                    "dateFormat": None,
                    "knownInAdvance": False
                },
                {
                    "name": "strFeat",
                    "featureType": "Text",
                    "importance": 0.3,
                    "dateFormat": None,
                    "knownInAdvance": False
                }
            ]
        }
    )


@pytest.fixture
def mock_project_features_api(datarobot_url, projectid):
    responses.get(
        f'{datarobot_url}projects/{projectid}/features/',
        json=[
            {
                "id": 1,
                "name": "numFeat",
                "featureType": "Numeric",
                "importance": 0.1,
                "mean": 0,
                "median": 0,
                "min": -1,
                "max": 1,
                "stdDev": 1,
                "projectId": projectid,
                "lowInformation": False,
                "uniqueCount": 100,
                "timeSeriesEligibilityReason": "notADate",
                "timeSeriesEligible": False,
            },
            {
                "id": 2,
                "name": "catFeat",
                "featureType": "Categorical",
                "importance": 0.2,
                "mean": None,
                "median": None,
                "min": None,
                "max": None,
                "stdDev": None,
                "projectId": projectid,
                "lowInformation": False,
                "uniqueCount": 100,
                "timeSeriesEligibilityReason": "notADate",
                "timeSeriesEligible": False,
            },
            {
                "id": 3,
                "name": "strFeat",
                "featureType": "Text",
                "importance": 0.3,
                "mean": None,
                "median": None,
                "min": None,
                "max": None,
                "stdDev": None,
                "projectId": projectid,
                "lowInformation": False,
                "uniqueCount": 100,
                "timeSeriesEligibilityReason": "notADate",
                "timeSeriesEligible": False,
            },
            # This is the target
            {
                "id": 4,
                "name": "targetFeat",
                "featureType": "Boolean",
                "importance": 1,
                "uniqueCount": 2,
                "mean": 0.4,
                "median": 0,
                "min": 0,
                "max": 1,
                "stdDev": 0.49,
                "projectId": projectid,
                "lowInformation": False,
                "timeSeriesEligibilityReason": "notADate",
                "timeSeriesEligible": False,
            },
            # This is a project feature which is not part of the deployment
            {
                "id": 5,
                "name": "whoCaresFeat",
                "featureType": "Text",
                "importance": 0.0,
                "mean": None,
                "median": None,
                "min": None,
                "max": None,
                "stdDev": None,
                "projectId": projectid,
                "lowInformation": False,
                "uniqueCount": 100,
                "timeSeriesEligibilityReason": "notADate",
                "timeSeriesEligible": False,
            },
        ],
    )


@pytest.fixture
def mock_feature_histogram_api(datarobot_url, projectid):
    responses.get(
        f'{datarobot_url}projects/{projectid}/featureHistograms/catFeat/',
        json={
            "plot": [
                {
                    "label": "==Missing==",
                    "count": 10,
                    "target": 0.35
                },
                {
                    "label": "cat1",
                    "count": 50,
                    "target": 0.83,
                },
                {
                    "label": "cat2",
                    "count": 40,
                    "target": 0.67,
                },
            ]
        }
    )


@pytest.fixture
def mock_prediction_server_api(datarobot_prediction_api_url, deploymentid, positive_class):
    responses.post(
        f'{datarobot_prediction_api_url}/predApi/v1.0/deployments/{deploymentid}/predictions?maxExplanations=12&maxNgramExplanations=all',
        json={'data': []}
    )


@responses.activate
@pytest.mark.usefixtures('setup_standard_env_vars', 'mock_version_api')
def test_create_prediction_form_with_env_vars(datarobot_url):
    """
    Verify that if we have the right environment variables that we will
    not have any errors
    """
    form = AppTest.from_file('../streamlit_app.py')
    form.run(timeout=30)
    assert not form.exception
    assert not form.error.values
    assert 'Included in this demo are two pages:' in form.main.children[1].value


def test_create_prediction_form():
    form = AppTest.from_file('../streamlit_app.py')
    form.run(timeout=30)
    assert not form.exception
    # Since we have no env vars plugged in, we have an error msg.
    assert form.error.values[0] == "Unable to setup local environment"
    assert form.error.values[
               1] == "Please make sure the 'token' environment variable is set to be a valid token from your DataRobot account"


@responses.activate
@pytest.mark.usefixtures(
    'setup_standard_env_vars',
    'mock_version_api',
    'mock_deployment_api',
    'mock_project_api',
    'mock_deployment_feature_api',
    'mock_project_features_api',
    'mock_feature_histogram_api',
    'mock_prediction_server_api'
)
def test_select_predictor_demo():
    form = AppTest.from_file('../streamlit_app.py')
    form.run(timeout=30)

    form.selectbox[0].select("Predictor Demo").run()
    # The single Numerical Feature
    set_num_feat = 12
    form.number_input[0].set_value(set_num_feat).run()
    assert form.number_input[0].label == "numFeat"
    # Categorical Feature
    set_categorical_feat = "cat1"
    select_box = next((sb for sb in form.selectbox if sb.label == "catFeat"))
    select_box.select(set_categorical_feat).run()
    # Text Feature
    set_text_feat = "This is a text feature"
    form.text_input[0].set_value(set_text_feat).run()
    assert form.text_input[0].label == "strFeat"
    # Ship that prediction off to DataRobot!
    form.main.button[0].click().run()

    # Get the request we sent to DR. For now, we can just look at the only POST
    # we have sent.
    sent_request = next((call for call in responses.calls if (call.request.method == 'POST')))
    sent_request_payload = json.loads(sent_request.request.body)[0]
    assert sent_request_payload[form.number_input[0].label] == set_num_feat
    assert sent_request_payload[form.selectbox[0].label] == set_categorical_feat
    assert sent_request_payload[form.text_input[0].label] == set_text_feat
