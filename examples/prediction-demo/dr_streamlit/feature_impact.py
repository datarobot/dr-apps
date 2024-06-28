import copy
from typing import Any, Optional

import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st
from altair import Undefined
from datarobot import TARGET_TYPE

from .caches import get_model, get_project, initialize_and_get_feature_impact
from .select_box import AGGREGATED_NAME
from .wrappers import chart_with_error_backup


@st.cache_data
def _get_aggregated_feature_impact_data(project_id: str, model_id: str):
    fi_data = initialize_and_get_feature_impact(
        project_id=project_id, model_id=model_id, use_multiclass=False
    )
    return pd.DataFrame.from_records(fi_data).sort_values('impactNormalized', ignore_index=True)


@st.cache_data
def _get_multiclass_feature_impact_data(project_id: str, model_id: str):
    aggregated_fi = _get_aggregated_feature_impact_data(
        project_id=project_id,
        model_id=model_id,
    )
    feature_impacts = [{'class': AGGREGATED_NAME, 'featureImpacts': aggregated_fi}]
    mc_fi_data = copy.copy(
        initialize_and_get_feature_impact(
            project_id=project_id, model_id=model_id, use_multiclass=True
        )
    )
    for entry in mc_fi_data:
        entry['featureImpacts'] = pd.DataFrame.from_records(entry['featureImpacts'])
        feature_impacts.append(entry)
    return feature_impacts


@chart_with_error_backup
def derived_features_chart(
    project_id: str,
    model_id: str,
    selected_class: Optional[str] = None,
    height: Any = None,
    width: Any = None,
):
    project = get_project(project_id)
    model = get_model(project_id=project_id, model_id=model_id)
    if project.target_type == TARGET_TYPE.MULTICLASS:
        feature_impacts = _get_multiclass_feature_impact_data(
            project_id=project_id, model_id=model_id
        )
        fig = px.bar(
            next(c['featureImpacts'] for c in feature_impacts if c['class'] == selected_class),
            y='featureName',
            x='impactNormalized',
            title=model.model_type,
            height=height,
            width=width,
        )
        return st.plotly_chart(fig)
    else:
        feature_impact = _get_aggregated_feature_impact_data(
            project_id=project_id, model_id=model_id
        )
        c = (
            alt.Chart(
                feature_impact,
                height=height if height else Undefined,
                width=width if width else Undefined,
            )
            .mark_bar()
            .encode(y=alt.Y('featureName', sort='-x'), x=alt.X('impactNormalized'))
        )
        return st.altair_chart(c)
