from typing import List, Optional

import streamlit as st
from datarobot import Project, TARGET_TYPE

from .caches import initialize_and_get_feature_impact, get_project

AGGREGATED_NAME = "Aggregated"


@st.cache
def _get_multiclass_names(project_id: str, model_id: str) -> List[str]:
    """
    Gets all multiclass names for a given model.
    There is no multiclass names API, so we just have to get them from another API and
    discard unused data. This is cached, so it'll only be slow once though.
    """
    feature_impact = initialize_and_get_feature_impact(project_id=project_id, model_id=model_id, use_multiclass=True)
    multiclass_names = [fi['class'] for fi in feature_impact]
    multiclass_names.append(AGGREGATED_NAME)
    return multiclass_names


def multiclass_dropdown_menu(project_id: str, model_id: str) -> Optional[str]:
    project = get_project(project_id)
    if project.target_type != TARGET_TYPE.MULTICLASS:
        return None
    all_classes = _get_multiclass_names(project_id, model_id)
    return st.sidebar.selectbox("Select a class:", all_classes)


@st.cache
def _get_text_feature_names(project_id: str) -> List[str]:
    features = Project(project_id).get_features()
    text_features = [feature.name for feature in features if feature.feature_type == 'Text']
    text_features.append(AGGREGATED_NAME)
    return text_features


def text_feature_dropdown_menu(project_id: str) -> str:
    all_text_features = _get_text_feature_names(project_id)
    return st.sidebar.selectbox("Select a text feature:", all_text_features)


@st.cache
def _get_models(project_id: str) -> List[str]:
    return [model.id for model in Project(project_id).get_models()]


def project_model_dropdown(project_id: str) -> str:
    all_model_ids = _get_models(project_id)
    return st.sidebar.selectbox("Select a model", all_model_ids)