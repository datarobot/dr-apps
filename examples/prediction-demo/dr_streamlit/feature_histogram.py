from typing import Optional, Any

import pandas as pd
from datarobot import FeatureHistogram
import streamlit as st
import plotly.express as px


@st.cache
def get_feature_histogram_data(project_id: str, feature_name: str, bin_limit: Optional[int] = 10):
    fh = FeatureHistogram.get(project_id=project_id, feature_name=feature_name, bin_limit=bin_limit)
    return pd.DataFrame.from_records(fh.plot)


def feature_histogram_chart(
        project_id: str,
        feature_name: str,
        fill_target: Optional[Any] = None,
        default_color: str = 'blue',
        fill_target_color: str = 'red',
        bin_limit: Optional[int] = None,
):
    """

    :param project_id: ID of the project that's being worked
    :param feature_name: The feature we are making a histogram of
    :param fill_target:  This is the label we want to color in.
    :param default_color: Default color of each bar
    :param fill_target_color: Default color of shaded bar
    :param bin_limit: Number of histogram bins (default == 60)
    :return:a plotly Figure of the feature histogram.

    """
    fh_df = get_feature_histogram_data(project_id, feature_name, bin_limit=bin_limit)
    colors = {c: default_color for c in fh_df['label']}
    if fill_target is not None:
        if isinstance(fill_target, (float,)):
            # Your float input might be 21.114, but the label is 21.11399999983.
            # For the time being we just have an imperfect implementation.
            fill_target_from_api = str(fill_target)
        elif isinstance(fill_target, (int,)):
            fill_target_from_api = str(float(fill_target))
        else:
            fill_target_from_api = fill_target
        if fill_target_from_api in colors:
            colors[fill_target_from_api] = fill_target_color
        else:
            colors['=All Other='] = fill_target_color
    fig = px.bar(
        fh_df,
        color='label',
        color_discrete_map=colors,
        x='label',
        y='count',
    )
    axis = {'visible': False, 'showticklabels': False}
    fig.update_layout(yaxis=axis, xaxis=axis)
    fig.update_traces(showlegend=False)
    return fig
