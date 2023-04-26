import base64

from typing import Dict, Any, List, Optional, Union, Tuple

import pandas as pd
import plotly.io
import streamlit as st
from pandas import Series

from dr_streamlit.caches import get_model_features
from dr_streamlit.feature_histogram import feature_histogram_chart


class PredictionExplanationTableColors:
    POSITIVE_COLOR = 'red'
    NEGATIVE_COLOR = 'blue'
    @classmethod
    def qs_to_span(cls, qualitative_strength: str) -> Union[Tuple[str, str], Tuple[None, None]]:
        color = None
        if '++' in qualitative_strength:
            color = cls.POSITIVE_COLOR
        elif '--' in qualitative_strength:
            color = cls.NEGATIVE_COLOR

        if color:
            return f':{color}[', ']'
        else:
            return None, None


def plotly_to_b64_img(plot, width: Optional[int] = None, height: Optional[int] = None) -> str:
    plot.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    img = plotly.io.to_image(plot, format='png', width=width, height=height, scale=1)
    return base64.encodebytes(img).decode().replace("\n", "")


def prediction_explanation_table(
        pex: pd.DataFrame,
        project_id: str,
        model_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        bin_limit: Optional[int] = None,
) -> None:
    feature_values = []
    charts = []
    for row in pex.itertuples():
        if hasattr(row, 'perNgramTextExplanations'):
            feature_values.append(color_in_features(row.featureValue, row.perNgramTextExplanations))
        else:
            feature_values.append(row.featureValue)

        if type(row.feature) is not dict:
            chart = feature_histogram_chart(project_id, row.feature, row.featureValue, bin_limit=bin_limit)
            charts.append(
                "![default](data:image/png;base64," + plotly_to_b64_img(chart, height=height, width=width) + ')')
        else:
            charts.append('')

    table = pd.DataFrame({'Feature': pex['feature'], 'Value': feature_values, 'Strength': qualitative_strength_from_prediction_explanations(pex, project_id=project_id, model_id=model_id),
                          'Distribution': charts})
    st.markdown(table.to_markdown())


def color_in_features(text_feature_value: str, per_ngram_text_explanations: List[Dict[str, Any]]) -> str:
    if not per_ngram_text_explanations:
        return text_feature_value
    all_ngrams = []
    for ngram_text_explanation in per_ngram_text_explanations:
        for ngram in ngram_text_explanation['ngrams']:
            all_ngrams.append(
                {
                    **ngram,
                    'qualitativeStrength': ngram_text_explanation['qualitativeStrength']
                }
            )
    all_ngrams.sort(key=lambda x: -x['endingIndex'])

    for ngram in all_ngrams:
        start = ngram['startingIndex']
        end = ngram['endingIndex']
        color_span, close_color_span = PredictionExplanationTableColors.qs_to_span(ngram['qualitativeStrength'])
        if color_span:
            text_feature_value = text_feature_value[:start] +\
                                 color_span + text_feature_value[start:end] + close_color_span +\
                                 text_feature_value[end:]

    return text_feature_value


def qualitative_strength_from_prediction_explanations(
        pex: pd.DataFrame, project_id: str, model_id: str
) -> Series:
    """
    This covers the xemp qualitative strength defined in the DR Docs here:
    https://docs.datarobot.com/en/docs/modeling/reference/model-detail/xemp-calc.html.
    Since we can't "grey out" +++ or --- we just leave those as empty features.

    :param pex: prediction explanations
    :param project_id: project associated with the prediction
    :param model_id: model associated with the prediction
    :return:
    """
    if not pex['qualitativeStrength'].isnull().values.all():
        return pex['qualitativeStrength']

    features = get_model_features(project_id=project_id, model_id=model_id)

    def strength_to_qualitative_strength(strength: float) -> str:
        positive_strength = strength > 0
        abs_strength = abs(strength)

        if len(features) == 1:
            if abs_strength > .001:
                return '+++' if positive_strength else '---'
            else:
                return ''
        if len(features) == 2:
            if abs_strength > 0.75:
                return '+++' if positive_strength else '---'
            elif abs_strength > .25:
                return '++' if positive_strength else '--'
            elif abs_strength > .001:
                return '+' if positive_strength else'-'
            else:
                return ''
        if len(features) < 10:
            if abs_strength > (2.0/len(features)):
                return '+++' if positive_strength else '---'
            elif abs_strength > 1.0 / (2.0 * len(features)):
                return '++' if positive_strength else '--'
            elif abs_strength > 0.001:
                return '+' if positive_strength else '-'
            else:
                return ''
        if len(features) >= 10:
            if abs_strength > 0.2:
                return '+++' if positive_strength else '---'
            elif abs_strength > .05:
                return '++' if positive_strength else '--'
            elif abs_strength > .001:
                return '+' if positive_strength else'-'
            else:
                return ''

        # Case shouldn't be reached
        return '+' if positive_strength else '-'

    return pex['strength'].apply(strength_to_qualitative_strength)

