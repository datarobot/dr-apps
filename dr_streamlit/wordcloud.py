from typing import Optional, Dict, Any

import plotly
import streamlit as st
import streamlit_wordcloud as wordcloud
from datarobot import Model
from datarobot.errors import ClientError
from datarobot.models.word_cloud import WordCloud

from dr_streamlit.select_box import AGGREGATED_NAME


def _get_word_cloud_data(project_id, model_id, exclude_stop_words=False) -> WordCloud:
    return Model(
        id=model_id,
        project_id=project_id
    ).get_word_cloud(exclude_stop_words=exclude_stop_words)


def _color(coefficent, scales):
    """
    Get color associated with a coefficent
    :param coefficent: a number between -1 and 1
    :param scales: A value from the plotly scales (eg: plotly.colors.PLOTLY_SCALES["RdBu"])
    :return: an rgb like 'rgb(106,137,247)'
    """
    unit = (coefficent + 1) / 2  # scale it from [-1,1] to a [0,1] domain
    assert 0 <= unit <= 1
    return [rgb for min_value, rgb in scales if unit >= min_value][-1]


def wordcloud_chart(
    project_id,
    model_id,
    specified_class: Optional[str] = None,
    selected_feature: Optional[str] = None,
    exclude_stop_words: bool = False,
    top_values: Optional[int] = None
) -> Dict[str, Any]:
    """

    :param project_id:
    :param model_id:
    :param specified_class:
    :param selected_feature:
    :param exclude_stop_words:
    :param top_values:
    :return:
    """
    try:
        word_cloud_object: WordCloud = _get_word_cloud_data(project_id=project_id, model_id=model_id, exclude_stop_words=exclude_stop_words)
    except ClientError as ce:
        if ce.json['message'] == 'No word cloud data was found for this model':
            st.text('This model does not support word cloud')
            return dict()
        raise
    if specified_class != AGGREGATED_NAME and specified_class:
        word_cloud_object = WordCloud(word_cloud_object.ngrams_per_class()[specified_class])
    if selected_feature != AGGREGATED_NAME and selected_feature:
        word_cloud_object.ngrams = filter(lambda d: d['variable'] in [f'NGRAM_OCCUR_L2_{selected_feature}', selected_feature], word_cloud_object.ngrams)

    if top_values:
        word_cloud_object = WordCloud(word_cloud_object.most_important(top_values))

    words = [dict(
        text=ngram['ngram'],
        value=ngram['count'],
        color=_color(ngram['coefficient'], scales=plotly.colors.PLOTLY_SCALES["RdBu"]),
        frequency=ngram['frequency'],
        coefficient=ngram['coefficient'],
    ) for ngram in word_cloud_object.ngrams]
    chart = wordcloud.visualize(words, tooltip_data_fields={
        'text': 'ngram', 'value': 'count', 'frequency': 'frequency', 'coefficient': 'coefficient'
    }, per_word_coloring=True, key=f'WordCloud{project_id}{model_id}{specified_class}{selected_feature}')
    return chart


