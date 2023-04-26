from typing import List, Dict, Any, Optional, cast
import streamlit as st
import numpy as np
import pandas as pd
from datarobot import Deployment, Project, TARGET_TYPE, BatchPredictionJob
from datarobot.client import get_client, Client

from dr_streamlit.caches import get_model


@st.cache
def submit_prediction(
        deployment: Deployment,
        prediction_data: pd.DataFrame,
        max_explanations: Optional[int] = None,
):
    """
    The DataRobot python public API does not have a predict method,
    so this is a basic implementation
    """
    client: Client = get_client()
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": client.headers["Authorization"],
        "DataRobot-Key": deployment.default_prediction_server['datarobot-key'],
    }

    rsp = client.request(
        method='post',
        url=f'{deployment.prediction_environment["name"]}/predApi/v1.0/deployments/{deployment.id}/predictions',
        data=prediction_data.to_json(orient="records"),
        params={
            "maxExplanations": max_explanations,
            "maxNgramExplanations": 'all'
        },
        headers=headers,
    )
    return rsp.json()


def _get_chart_from_model_or_parent(project_id: str, model_id: str, chart: str):
    """
    Some models are retrained from other models and do not retain some things like the
    """
    client: Client = get_client()
    roc_curve_rsp = client.get(f'projects/{project_id}/models/{model_id}/{chart}/')
    roc_curve_rsp.raise_for_status()
    roc_curve_rsp_json = roc_curve_rsp.json()
    if not roc_curve_rsp_json['charts']:
        model = get_model(project_id, model_id)
        return _get_chart_from_model_or_parent(project_id, model.parent_model_id, chart)
    else:
        return roc_curve_rsp_json

@st.cache
def submit_batch_prediction(deployment: Deployment, df: pd.DataFrame, max_explanations: int):
    [_, result] = BatchPredictionJob.score_pandas(
        deployment=deployment,
        df=df,
        max_explanations=max_explanations,
    )
    project = Project.get(deployment.model['project_id'])
    target = project.target
    scored_predictions = []
    for row in result.itertuples():
        record = dict()
        if project.target_type == TARGET_TYPE.BINARY:
            record['predictionValues'] = [
                {'value': getattr(row, f'{target}_{index}_PREDICTION'), 'label': float(index)} for index in [0, 1]
            ],
        elif project.target_type == TARGET_TYPE.REGRESSION:
            record['prediction'] = getattr(row, f'{target}_PREDICTION')
        else:
            raise ValueError("Target Type not supported")
        record['predictionExplanations'] = [
                {
                    'feature': getattr(row, f'EXPLANATION_{i}_FEATURE_NAME'),
                    'featureValue': getattr(row, f'EXPLANATION_{i}_ACTUAL_VALUE'),
                    'strength': getattr(row, f'EXPLANATION_{i}_STRENGTH'),
                    'qualitativeStrength': getattr(row, f'EXPLANATION_{i}_QUALITATIVE_STRENGTH'),
                } for i in range(1, max_explanations + 1) if hasattr(row, f'EXPLANATION_{i}_FEATURE_NAME')
            ]
        scored_predictions.append(record)

    return {'data': scored_predictions}


@st.cache
def get_distribution_chart_data(project_id: str, model_id: str, specified_class: Optional[str] = None):
    project = Project.get(project_id=project_id)
    if project.target_type == TARGET_TYPE.BINARY:
        roc_curve_rsp_json = _get_chart_from_model_or_parent(project_id=project_id, model_id=model_id, chart='rocCurve')
        validation_chart = next(chart for chart in roc_curve_rsp_json['charts'] if chart['source'] == 'validation')
        prediction_data = validation_chart['negativeClassPredictions'] + validation_chart['positiveClassPredictions']
        return _prediction_data_to_bins_for_binary(prediction_data)
    elif project.target_type == TARGET_TYPE.REGRESSION:
        lift_chart_rsp_json = _get_chart_from_model_or_parent(project_id=project_id, model_id=model_id, chart='liftChart')
        validation_chart = next(chart for chart in lift_chart_rsp_json['charts'] if chart['source'] == 'validation')
        return _prediction_data_to_bins_for_regression(unnormalize_prediction(validation_chart['bins']))
    elif project.target_type == TARGET_TYPE.MULTICLASS:
        multiclass_chart_rsp = _get_chart_from_model_or_parent(project_id=project_id, model_id=model_id, chart='multiclassLiftChart')
        validation_chart = next(chart for chart in multiclass_chart_rsp['charts'] if chart['source'] == 'validation')
        specified_class_bin = next(class_bin['bins'] for class_bin in validation_chart['classBins'] if class_bin['targetClass'] == specified_class)
        return _prediction_data_to_bins_for_regression(unnormalize_prediction(specified_class_bin))
    raise ValueError(f'{project.target_type} is not supported')


def _prediction_data_to_bins_for_binary(
        prob_data: List[float], bins_num: int = 20
) -> List[Dict[str, Any]]:
    """
    Converts list with probabilities to bins with distribution data of
    probability from 0 to 1.

    :param prob_data: list with probabilities.
    :param bins_num: number of output bins.

    :return: List with bin objects.
    """

    zero_bound_added = False
    one_bound_added = False

    if 0 not in prob_data:
        prob_data += [0]
        zero_bound_added = True

    if 1 not in prob_data:
        prob_data += [1]
        one_bound_added = True

    bins = _prediction_data_to_bins_for_regression(prob_data, bins_num)

    if zero_bound_added:
        bins[0]['total_freq'] -= 1

    if one_bound_added:
        bins[-1]['total_freq'] -= 1

    return bins


def _prediction_data_to_bins_for_regression(
        prediction_data: List[float], bins_num: int = 20
) -> List[Dict[str, List[float]]]:
    """
    Counts distribution of prediction data.

    :param prediction_data: list with prediction results.
    :param bins_num: number of output bins.

    :return: List with bin objects.
    """

    values, bounds = np.histogram(prediction_data, bins_num)
    return [
        {
            'bin': bounds[idx].item(),
            'total_freq': value.item(),
        }
        for idx, value in enumerate(values)
    ]


def unnormalize_prediction(bins: List[Dict[str, Any]]) -> List[float]:
    """
    Returns list of unnormalized predictions from distribution bins

    :param bins: list of bins from lift chart or roc curve
    """
    return cast(List[float], [_bin['predicted'] for _bin in bins])
