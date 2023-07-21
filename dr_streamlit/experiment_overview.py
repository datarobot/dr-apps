from typing import Optional, Dict, Any

import streamlit as st
from datarobot.client import get_client


def get_experiment_name_and_desc(project_id: str) -> Optional[Dict[str, Any]]:
    client = get_client()
    rsp_json = client.get(f'experimentContainers/?projectId={project_id}').json()
    if len(rsp_json['data']):
        return rsp_json['data'][0]
    else:
        return None

def experiment_container_overview_widget(project_id):
    experient_container_overview = get_experiment_name_and_desc(project_id)
    if not experient_container_overview:
        return None

    st.markdown(f"""
# {experient_container_overview['name']}
    
### {experient_container_overview['description']}
    """)