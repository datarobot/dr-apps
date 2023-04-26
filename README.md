# What's Included
There are two basic Streamlit demos in this app:

#### insights demo
This application allows users to submit a single prediction using the realtime DataRobot generated prediction explanations and color-coded n-grams. Some projects, such as SHAP projects, need to use the batch prediction API. 

#### predictor demo 
This application allows users to view models in the leaderboard as well as word cloud and feature impact charts. The word cloud also offers a special breakdown for individual text features.

## What's supported
Currently, the following project types are supported: 
* Multiclass
* Regression
* Binary classification
* Feature Discovery

Other project types may work, however, they have not been tested.
The Insights app supports:

* Time Series regression 
* Cold start
* Segmented modeling
* Anomaly detection

The Insights app will generate a word cloud for some models with text. Note that a word cloud is not generated for all models.
The Predictor app does not support time series projects.
## Getting Started
### Create your GitHub repository 
1. (Optional) While in the `dr-streamlit` repository, click **Fork** at the top of the page and skip to the section **Create a Streamlit app**.
2. In the `dr-streamlit` repository, click **Code** and select **Download ZIP**.
3. Navigate to your GitHub repositories and click **New repository**.
4. Create a repository. Depending on your Streamlit account you may need to make this repository public, but Streamlit allows you to deploy private repositories, assuming you are signed in and the authentication is linked. 
5. In your new repository, open the **Code** tab.
6. Click **Add file > Upload files** and either upload the entire ZIP or specific files (from the ZIP downloaded in step 2).

### Create a Streamlit app
1. Navigate your web browser to https://share.streamlit.io . If you do not have a Streamlit account, sign up for one. 
2. Click **New App > From existing repo**.
3. Confirm that your Github and Streamlit accounts are connected. For help, refer to the Streamlit documentation: https://blog.streamlit.io/host-your-streamlit-app-for-free/. Once connected, Streamlit will be able to read in the files in your repo.
4. In the **Deploy an app** window, populate the following fields:
* Under **Repository**, enter the name of your new Github repository (from step 4).
* Under **Branch**, choose **main**.
* Under **Main File Path**, add the .py file with your Streamlit app code. Alternatively, you can use the default **streamlit_app.py** provided.
* Click the advanced settings icon (the three dots located in the Manage App menu). The next section describes how to set up your environment. .

### Connecting DataRobot to the app:
1. In DataRobot, open the appropriate project and click Models to open the Leaderboard. 
2. Copy the series of numbers and letters that follow projects/ in the URL (e.g., app.datarobot.com/projects/(projectid)/models/(modelid)/blueprint ).
3. Click **Deployments** at the top of the page, select the deployment you want to use, and copy the ID in the URL (e.g., app.datarobot.com/deployments/(deploymentid)/overview)
4. In Streamlit, open **Advanced Settings > Secrets > Text box** and enter those values:

```
projectid = "<insert copied project ID number here>"
deploymentid = = "<insert copied deployment ID here>"
```
Example: 
```
projectid = “64496945bb321d719cac6451”
deploymentid = “64496952bb321d719cac6452”
```

5. In DataRobot, click your **User icon** in the top right corner and select **Developer tools**. Then, select any of the API keys shown.
6. In Streamlit, return to the **Secrets** page and enter the token:
Example:
```
projectid = “64496945bb321d719cac6451”
deploymentid = “64496952bb321d719cac6452”

token = "644969e2bb321d719cac6455644969e2bb321d719cac6456644969e2bb321"
```
7. Once set, hit **Deploy!** and wait for your app to populate. 

### Running on a Local Computer
The required dependencies are defined in `requirements.txt`. In your favorite package manager, install the dependencies:
```
pip install -r requirements.txt.
```
Supply the token, project id, or deployment id. These can either be hard set in the code or be environment variables (e.g., `token`, `projectid`, `deploymentid`). The project ID and deployment ID are part of the URL in DataRobot, and developer tokens are located in your Developer tools (https://app.datarobot.com/account/developer-tools). See the *Connecting DataRobot to the app* section for step-by-step instructions.