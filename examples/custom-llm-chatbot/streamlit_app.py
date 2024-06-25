import os

import datarobot as dr
import requests
import streamlit as st

API_URL = os.getenv('API_URL')
API_KEY = os.getenv('API_KEY')
DATAROBOT_KEY = os.getenv('DATAROBOT_KEY')
LLM_DEPLOYMENT_ID = os.getenv('LLM_DEPLOYMENT_ID')
DR_ENDPOINT = os.getenv('DR_ENDPOINT')


class DataRobotPredictionError(Exception):
    """Raised if there are issues getting predictions from DataRobot"""


def _raise_dataroboterror_for_status(response):
    """Raise DataRobotPredictionError if the request fails along with the response returned"""
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        err_msg = '{code} Error: {msg}'.format(code=response.status_code, msg=response.text)
        raise DataRobotPredictionError(err_msg)


def setup():
    try:
        c = dr.Client(
            token=API_KEY,
            endpoint=DR_ENDPOINT,
        )
        dr.client.set_client(c)
    except ValueError as e:
        st.error("Unable to setup local environment")
        if not API_KEY:
            st.error(
                "Please make sure the 'API_KEY' environment variable is set and is valid",
                icon='🔐',
            )
        if not API_URL:
            st.error(
                "Please make sure the 'API_URL' environment variable is set and is valid",
                icon='🔐',
            )
        if not DATAROBOT_KEY:
            st.error(
                "Please make sure the 'DATAROBOT_KEY' environment variable is set and is valid",
                icon='🔐',
            )
        if not DR_ENDPOINT:
            st.error(
                "Please make sure the 'DR_ENDPOINT' environment variable is set and is valid",
                icon='🔐',
            )
        if not LLM_DEPLOYMENT_ID:
            st.error(
                'The `LLM_DEPLOYMENT_ID` environment variable must be set to use the app',
                icon='🚨',
            )
        elif str(e) == 'The client is not compatible with the server version':
            st.error(
                """
            The API_KEY + endpoint pair provided is not valid.
            If you use eu datarobot, you will need to set 'endpoint' environment variable to
            https://app.eu.datarobot.com/api/v2/
            otherwise your API_KEY is not active.
            """,
                icon='🔐',
            )
    except Exception as e:
        st.error("Unable to setup local environment")
        st.error(str(e))


def llm_chatbot():
    st.write("# Welcome to Custom Deployed LLM Chatbot! 👋")
    st.markdown("<br><br>", unsafe_allow_html=True)

    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {}'.format(API_KEY),
        'DataRobot-Key': DATAROBOT_KEY,
    }
    url = API_URL.format(deployment_id=LLM_DEPLOYMENT_ID)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_input_key' not in st.session_state:
        st.session_state.current_input_key = 0

    for i, (user_input, bot_response) in enumerate(st.session_state.chat_history):
        st.text_input("You:", value=user_input, key=f"fixed_input_{i}", disabled=True)
        st.write(bot_response)
        st.markdown("<br>", unsafe_allow_html=True)

    with st.form(key=f"chat_form_{st.session_state.current_input_key}"):
        user_input = st.text_input(
            "How can I assist you today?", key=f"user_input_{st.session_state.current_input_key}"
        )
        submit_button = st.form_submit_button("Send")
        data = f'[{{"promptText": "{user_input}"}}]'

    if submit_button:
        if user_input:
            predictions_response = requests.post(
                url,
                headers=headers,
                data=data,
            )
            response = predictions_response.json()["data"][0]["prediction"]

            st.session_state.chat_history.append((user_input, response))
            st.session_state.current_input_key += 1
            st.experimental_rerun()
        else:
            st.warning("Please enter a message.")


if __name__ == "__main__":
    setup()
    llm_chatbot()
