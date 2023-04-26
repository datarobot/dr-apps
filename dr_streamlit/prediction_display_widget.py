from typing import Optional

import pandas as pd

from dr_streamlit.prediction_distribution import prediction_distribution_chart
from dr_streamlit.prediction_explanations_table import prediction_explanation_table
import streamlit as st


def prediction_display_chart(
    project_id: str,
    model_id: str,
    prediction: float,
    pex: pd.DataFrame,
    max_height: int,
    max_width: int,
    explanations: int = 12,
    bin_limit: Optional[int] = None,
    specified_class: Optional[str] = None
):
    if specified_class:
        st.header(specified_class)
    col_1, col_2, = st.columns([4, 8])
    with col_1:
        fig = prediction_distribution_chart(model_id=model_id, project_id=project_id, prediction=prediction, specified_class=specified_class)
        fig.update_layout(
            width=max_width,
            height=max_height,
        )
        col_1.plotly_chart(fig, use_container_width=True)
    with col_2:
        prediction_explanation_table(
            pex,
            project_id,
            model_id=model_id,
            height=int(max_height / explanations),
            width=int(max_width / explanations),
            bin_limit=bin_limit,
        )
