#!/usr/bin/env bash

export projectid=<projectid>
export deploymentid=<deploymentid>
export token="$DATAROBOT_API_TOKEN"
export endpoint="$DATAROBOT_ENDPOINT"
streamlit run --server.port 8080 streamlit_app.py
