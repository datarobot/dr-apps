import streamlit as st
from datarobot import Deployment


@st.cache
def get_deployment(deployment_id: str) -> Deployment:
    return Deployment.get(deployment_id)
