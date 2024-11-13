from typing import Any, Dict, List, Union

import streamlit as st
from datarobot import Deployment, FeatureImpactJob, Model, Project
from datarobot.errors import ClientError


def get_project(project_id: str) -> Project:
    return Project.get(project_id)


@st.cache_data
def get_model(project_id: str, model_id: str) -> Model:
    return Model.get(project_id, model_id)


@st.cache_data
def get_deployment(deployment_id: str) -> Deployment:
    return Deployment.get(deployment_id)


@st.cache_data
def get_model_features(project_id: str, model_id: str) -> List[str]:
    return Model(project_id=project_id, id=model_id).get_features_used()


@st.cache_data
def initialize_and_get_feature_impact(
    project_id: str, model_id: str, use_multiclass: bool
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    model = Model(id=model_id, project_id=project_id)

    def get_feature_impact():
        if use_multiclass:
            return model.get_multiclass_feature_impact()
        else:
            return model.get_feature_impact()

    try:
        return get_feature_impact()
    except ClientError as ce:
        if 'message' in ce.json and 'No feature impact data found for model' in ce.json['message']:
            fi_job = model.request_feature_impact()
            fi_job.wait_for_completion()
            return get_feature_impact()
        elif 'message' in ce.json and 'Feature Impact is in progress' in ce.json['message']:
            fi_job = FeatureImpactJob.get(project_id, ce.json['jobId'], with_metadata=False)
            fi_job.wait_for_completion()
            return get_feature_impact()
        else:
            raise
