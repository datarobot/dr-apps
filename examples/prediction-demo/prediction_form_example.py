import os

import streamlit as st
from datarobot import Deployment, Project, TARGET_TYPE
from datarobot.client import set_client, Client
import pandas as pd
from dr_streamlit import create_prediction_form, prediction_display_chart


if __name__ == '__main__':
    c = Client(
        token=os.getenv("token"),
        endpoint=os.getenv('endpoint', 'https://app.datarobot.com/api/v2/')
    )
    set_client(c)
    deployment_id = os.getenv('deploymentid')
    deployment = Deployment.get(deployment_id)
    project = Project.get(deployment.model['project_id'])
    use_bp_api = st.checkbox('Use Batch Prediction API')
    pred = create_prediction_form(deployment, deployment.model['project_id'], use_batch_prediction_api=use_bp_api)
    if pred:
        predicted_class = None  # For Multiclass
        if project.target_type == TARGET_TYPE.BINARY:
            prediction_values = pred['data'][0]['prediction_values']
            if type(prediction_values[0]) in [tuple, list]:
                # Some are like this
                prediction_values = prediction_values[0]
            prediction = next(pred_value['value'] for pred_value in prediction_values if pred_value['label'] == 0.0)
        elif project.target_type == TARGET_TYPE.REGRESSION:
            prediction = pred['data'][0]['prediction']
        elif project.target_type == TARGET_TYPE.MULTICLASS:
            predicted_class = pred['data'][0]['prediction']
            prediction = next(pv['value'] for pv in pred['data'][0]['prediction_values'] if pv['label'] == predicted_class)
        else:
            raise ValueError(f'{project.target_type} is not supported')

        pex = pd.DataFrame.from_records(pred['data'][0]['prediction_explanations'])
        prediction_display_chart(
            project_id=deployment.model['project_id'],
            model_id=deployment.model['id'],
            pex=pex,
            prediction=prediction,
            max_width=800,
            max_height=800,
            bin_limit=60,
            specified_class=predicted_class,
        )