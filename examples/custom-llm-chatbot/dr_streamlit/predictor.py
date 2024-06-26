import json

import streamlit as st
from datarobot import Deployment
from datarobot.client import Client, get_client


@st.cache
def submit_prediction(deployment: Deployment, prediction_data: json):
    client: Client = get_client()
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": client.headers["Authorization"],
        "DataRobot-Key": deployment.default_prediction_server['datarobot-key'],
    }
    url = f'{deployment.prediction_environment["name"]}/predApi/v1.0/deployments/{deployment.id}/predictions'
    response = client.request(
        method='post',
        url=url,
        data=prediction_data,
        headers=headers,
    )
    return response.json()


@st.cache
def get_response(deployment: Deployment, prediction_data: json):
    response = submit_prediction(deployment, prediction_data)
    try:
        return response["data"][0]["prediction"]
    except KeyError as e:
        st.error(e)
