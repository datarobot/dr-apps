from datetime import datetime
from typing import Dict, Any, List

import pandas
import streamlit as st
from datarobot import Deployment, FeatureHistogram, Project

from .predictor import submit_prediction, submit_batch_prediction


@st.cache
def get_prediction_features(project_id: str, deployment_id: str) -> List[Dict[str, Dict[str, Any]]]:
    deployment_features = Deployment(deployment_id).get_features()
    project_features = Project(project_id).get_features()
    prediction_features = list()
    for d_feature in deployment_features:
        project_feature = next(p_feature for p_feature in project_features if p_feature.name == d_feature['name'])
        record = {
            'name': d_feature['name'],
            'feature_type': d_feature['feature_type'],
            'date_format': project_feature.date_format,
            'min': project_feature.min,
            'max': project_feature.max,
            'median': project_feature.median,
            'suspected_int': all(
                type(f) == int for f in [project_feature.max, project_feature.min, project_feature.max]
            )
        }
        if d_feature['feature_type'] == 'Categorical':
            histogram = FeatureHistogram.get(project_id=project_id, feature_name=d_feature['name'])
            record['options'] = [option['label'] for option in histogram.plot]
        prediction_features.append(record)

    return prediction_features


def create_prediction_form(
        deployment: Deployment,
        project_id: str,
        use_batch_prediction_api=False,
        n_cols=4,
        max_explanations=12
):
    feats = get_prediction_features(project_id, deployment.id)
    pred = dict(index=[0])
    cols = st.columns(n_cols)
    with st.form("prediction_form", clear_on_submit=False):
        for index, f in enumerate(feats):
            with cols[index % n_cols]:
                if f['feature_type'] == "Text":
                    pred[f['name']] = st.text_input(f['name'])
                elif f['feature_type'] == "Numeric":
                    pred[f['name']] = st.number_input(
                        f['name'],
                        value=int(f['median']) if f['suspected_int'] else float(f['median']),
                        step=1 if f['suspected_int'] else 0.01
                    )
                elif f['feature_type'] == "Categorical":
                    pred[f['name']] = st.selectbox(f['name'], options=f['options'])
                elif f['feature_type'] == "Date":
                    date: datetime = st.date_input(f['name'])
                    pred[f['name']] = date.strftime(f['date_format']) if date else ''
                elif f['feature_type'] == "Boolean":
                    pred[f['name']] = st.selectbox(f['name'], options=[True, False])
                elif f['feature_type'] == 'Percentage':
                    pred[f['name']] = st.text_input(
                        f['name'],
                        value= f['median'],
                    )

        # Now add a submit button to the form:
        v = st.form_submit_button("Submit")
        if v:
            if use_batch_prediction_api:
                return submit_batch_prediction(deployment, pandas.DataFrame.from_dict(pred), max_explanations)
            else:
                return submit_prediction(deployment, pandas.DataFrame.from_dict(pred), max_explanations)
