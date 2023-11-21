import pandas as pd
import streamlit as st
import os
from datarobot import Client, TARGET_TYPE
from datarobot.client import set_client
from dr_streamlit import multiclass_dropdown_menu, derived_features_chart, text_feature_dropdown_menu, \
    project_model_dropdown, wordcloud_chart, get_deployment, get_project, create_prediction_form, \
    prediction_display_chart, experiment_container_overview_widget
from dr_streamlit.datarobot_branding import datarobot_logo

deployment_id = os.getenv('deploymentid')
project_id = os.getenv('projectid')


def intro():

    st.write("# Welcome to DataRobot's Streamlit package! 👋")
    st.sidebar.success("Select a demo above.")

    if not deployment_id:
        st.error('The deploymentid environment variable must be set to use the predictor demo', icon='🚨')
    if not project_id:
        st.error('The projectid environment variable must be set', icon='🚨')

    st.markdown(
        """
        Included in this demo are two pages: a predictor demo and an insights demo. 
        
        The predictor demo comes with: 
         * A form to adjust prediction features
         * A distribution of where that falls in the holdout data
         * A table of prediction explanations
         * A histogram of where the input features compare to features inside the training data. 
         * Colored nGrams for text features
         
        The predictor app also lets you toggle between the single (AKA real-time) and batch prediction API. 
        Some deployments (like SHAP) require some more setup to get the single prediction API working, so this toggle
        can be an easy way to use it.  
        
        The insights demo comes with:
        * A model selector for all the models in the project's leaderboard
        * A class selector for all the classes in the project if it's multiclass
        * A feature impact chart
        * A word cloud (if your project has text features and the  model has a word cloud) which can be toggled
        between various text features of your project. 
        
        """
    )


def insights_app():
    model_id = project_model_dropdown(project_id)
    selected_class = multiclass_dropdown_menu(project_id, model_id)
    selected_feature = text_feature_dropdown_menu(project_id)
    experiment_container_overview_widget(project_id)
    wordcloud_chart(
        project_id=project_id,
        model_id=model_id,
        specified_class=selected_class,
        selected_feature=selected_feature,
    )
    derived_features_chart(
        project_id=project_id,
        model_id=model_id,
        selected_class=selected_class,
        height=350,
        width=750
    )


def predictor_app():
    deployment = get_deployment(deployment_id)
    project = get_project(deployment.model['project_id'])
    use_bp_api = st.checkbox('Use Batch Prediction API')
    pred = create_prediction_form(deployment, deployment.model['project_id'], use_batch_prediction_api=use_bp_api)
    if pred:
        predicted_class = None  # For Multiclass
        if project.target_type == TARGET_TYPE.BINARY:
            prediction_values = pred['data'][0]['prediction_values']
            if type(prediction_values[0]) in [tuple, list]:
                # Some are like this
                prediction_values = prediction_values[0]
            # Assign prediction for the positive class label
            prediction = next(pred_value['value'] for pred_value in prediction_values if pred_value['label'] == project.positive_class)
        elif project.target_type == TARGET_TYPE.REGRESSION:
            prediction = pred['data'][0]['prediction']
        elif project.target_type == TARGET_TYPE.MULTICLASS:
            predicted_class = pred['data'][0]['prediction']
            prediction = next(pv['value'] for pv in pred['data'][0]['prediction_values'] if pv['label'] == predicted_class)
        else:
            raise ValueError(f'{project.target_type} is not supported')

        pex = pd.DataFrame.from_records(pred['data'][0]['prediction_explanations'])
        prediction_display_chart(
            project_id=deployment.model['project_id'],
            model_id=deployment.model['id'],
            pex=pex,
            prediction=prediction,
            max_width=800,
            max_height=800,
            bin_limit=60,
            specified_class=predicted_class,
        )


def main():
    try:
        c = Client(
            token=os.getenv("token"),
            endpoint=os.getenv('endpoint', 'https://app.datarobot.com/api/v2/')
        )
        set_client(c)
    except ValueError as e:
        st.error("Unable to setup local environment")
        if not os.getenv('token'):
            st.error("Please make sure the 'token' environment variable is set to be a valid token from your DataRobot account", icon='🔐')
        elif str(e) == 'The client is not compatible with the server version':
            st.error("""
            The token + endpoint pair provided is not valid.
            If you use eu datarobot, you will need to set 'endpoint' environment variable to
            https://app.eu.datarobot.com/api/v2/
            otherwise your token is not active.
            """,
                     icon='🔐')
    except Exception as e:
        st.error("Unable to setup local environment")
        st.error(str(e))
    else:
        page_names_to_funcs = {
            "—": intro,
            "Insights Demo": insights_app,
        }
        if deployment_id:
            page_names_to_funcs["Predictor Demo"] = predictor_app

        st.sidebar.markdown(
            datarobot_logo(),
            unsafe_allow_html=True,
        )
        demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
        page_names_to_funcs[demo_name]()


if __name__ == '__main__':
    main()
