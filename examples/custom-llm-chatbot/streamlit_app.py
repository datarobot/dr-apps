import os

import streamlit as st
from datarobot.client import Client, set_client
from dr_streamlit import get_deployment, get_response

DATAROBOT_API_TOKEN = os.getenv('DATAROBOT_API_TOKEN')
DATAROBOT_ENDPOINT = os.getenv('DATAROBOT_ENDPOINT')
LLM_DEPLOYMENT_ID = os.getenv('DEPLOYMENT_ID')


def setup():
    try:
        c = Client(
            token=DATAROBOT_API_TOKEN,
            endpoint=DATAROBOT_ENDPOINT,
        )
        set_client(c)
        return True
    except ValueError as e:
        st.error("Unable to setup local environment")
        if not DATAROBOT_API_TOKEN:
            st.error(
                "Please make sure the 'DATAROBOT_API_TOKEN' environment variable is set and is valid",
                icon='🔐',
            )
        if not LLM_DEPLOYMENT_ID:
            st.error(
                'The `DEPLOYMENT_ID` environment variable must be set to use the app',
                icon='🚨',
            )
        elif str(e) == 'The client is not compatible with the server version':
            st.error(
                """
            The DATAROBOT_API_TOKEN + endpoint pair provided is not valid.
            If you use eu datarobot, you will need to set 'endpoint' environment variable to
            https://app.eu.datarobot.com/api/v2/
            otherwise your DATAROBOT_API_TOKEN is not active.
            """,
                icon='🔐',
            )
    except Exception as e:
        st.error("Unable to setup local environment")
        st.error(str(e))


def llm_chatbot():
    st.set_page_config(page_title="Custom LLM Chatbot")
    st.write("# Welcome to Custom Deployed LLM Chatbot! 👋")
    st.markdown("<br><br>", unsafe_allow_html=True)

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
            deployment = get_deployment(LLM_DEPLOYMENT_ID)
            llm_response = get_response(deployment, data)

            st.session_state.chat_history.append((user_input, llm_response))
            st.session_state.current_input_key += 1
            st.experimental_rerun()
        else:
            st.warning("Please enter a message.")


if __name__ == "__main__":
    if setup():
        llm_chatbot()
