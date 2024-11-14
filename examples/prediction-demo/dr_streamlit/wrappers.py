import streamlit as st
from datarobot.errors import ClientError


def chart_with_error_backup(chart_func):
    def wrapper(*args, **kwargs):
        try:
            return chart_func(*args, **kwargs)
        except ClientError as ce:
            if 'message' in ce.json:
                return st.error(ce.json['message'])
            raise

    return wrapper
