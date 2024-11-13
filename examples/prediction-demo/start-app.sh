#!/usr/bin/env bash

export projectid=6710e5f7759307e559239e92
export deploymentid=66a0b4c10339206299eeddaf
export token="$DATAROBOT_API_TOKEN"
export endpoint="$DATAROBOT_ENDPOINT"
streamlit run --server.port 8080 streamlit_app.py