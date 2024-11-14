from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import streamlit as st
import wordcloud
from datarobot import Model
from datarobot.errors import ClientError
from datarobot.models.word_cloud import WordCloud

from .select_box import AGGREGATED_NAME


def _get_word_cloud_data(project_id, model_id, exclude_stop_words=False) -> WordCloud:
    return Model(id=model_id, project_id=project_id).get_word_cloud(
        exclude_stop_words=exclude_stop_words
    )


def wordcloud_chart(
    project_id,
    model_id,
    specified_class: Optional[str] = None,
    selected_feature: Optional[str] = None,
    exclude_stop_words: bool = False,
    top_values: Optional[int] = None,
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
        word_cloud_object: WordCloud = _get_word_cloud_data(
            project_id=project_id, model_id=model_id, exclude_stop_words=exclude_stop_words
        )
    except ClientError as ce:
        if 'message' in ce.json and ce.json['message'] == 'No word cloud data was found for this model':
            st.text('This model does not support word cloud')
            return dict()
        raise
    if specified_class != AGGREGATED_NAME and specified_class:
        word_cloud_object = WordCloud(word_cloud_object.ngrams_per_class()[specified_class])
    if selected_feature != AGGREGATED_NAME and selected_feature:
        word_cloud_object.ngrams = filter(
            lambda d: d['variable'] in [f'NGRAM_OCCUR_L2_{selected_feature}', selected_feature],
            word_cloud_object.ngrams,
        )

    if top_values:
        word_cloud_object = WordCloud(word_cloud_object.most_important(top_values))

    word_frequencies = {item["ngram"]: item["frequency"] for item in word_cloud_object.ngrams if
                        not item["is_stopword"]}

    cloud = wordcloud.WordCloud(background_color='#0e1117', width=1600, height=800,
                                random_state=42).generate_from_frequencies(word_frequencies)

    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    ax.imshow(cloud, interpolation='bilinear')
    ax.axis('off')
    fig.patch.set_facecolor('#0e1117')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    st.pyplot(fig, use_container_width=True)
