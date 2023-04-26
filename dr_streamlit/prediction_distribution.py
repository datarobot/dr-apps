from typing import Optional

import pandas as pd
from datarobot import Model, Project, TARGET_TYPE

from dr_streamlit.predictor import get_distribution_chart_data
import plotly.graph_objects as go


def prediction_distribution_chart(project_id: str, model_id: str, prediction: float, specified_class: Optional[str] = None) -> go.Figure:
    distribution_chart_data = get_distribution_chart_data(project_id, model_id, specified_class=specified_class)
    model = Model.get(project=project_id, model_id=model_id)
    prob_dist_df = pd.DataFrame.from_records(distribution_chart_data)
    project = Project.get(project_id)
    pred_max = prob_dist_df["total_freq"].max()
    fig = go.Figure()
    if project.target_type == TARGET_TYPE.BINARY:
        midline_index = prob_dist_df.loc[prob_dist_df["bin"] <= model.prediction_threshold].index.max()
        fig.add_trace(
            go.Scatter(
                y=list(prob_dist_df["bin"][: midline_index + 1]),
                x=list(prob_dist_df["total_freq"][: midline_index + 1]),
                mode="lines",
                fill="tozerox",
                fillcolor="rgba(60, 163, 232, 0.4)",
                marker=dict(color="#3CA3E8"),
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                y=list(prob_dist_df["bin"][midline_index:]),
                x=list(prob_dist_df["total_freq"][midline_index:]),
                mode="lines",
                fill="tozerox",
                fillcolor="rgba(230, 77, 77, 0.4)",
                marker=dict(color="#E64D4D"),
                showlegend=False,
            )
        )
    else:
        fig.add_trace(
            go.Scatter(
                y=list(prob_dist_df["bin"]),
                x=list(prob_dist_df["total_freq"]),
                mode="lines",
                fill="tozerox",
                fillcolor="rgba(230, 77, 77, 0.4)",
                marker=dict(color="#E64D4D"),
                showlegend=False,
            )
        )
    fig.add_hline(
        y=prediction,
        line_width=0.75,
        line_color="black",
    )
    fig.update_layout(
        margin=dict(t=0, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        xaxis_visible=False,
    )
    fig.update_yaxes(zeroline=False)
    fig.add_annotation(
        y=prediction,
        x=pred_max,
        text="PREDICTION",
        font=dict(
            size=14,
            color="black",
        ),
        showarrow=False,
        align="left",
        xshift=10,
        yshift=-20 if prediction > model.prediction_threshold else 35,
    )
    fig.add_annotation(
        y=prediction,
        x=pred_max,
        text=f"<b>{prediction :.3f}</b>",
        font=dict(size=24, color="black"),
        showarrow=False,
        align="left",
        xshift=10,
        yshift=-40 if prediction > model.prediction_threshold else 15,
    )
    return fig
