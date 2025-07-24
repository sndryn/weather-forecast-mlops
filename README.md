# Weather Forecast ML Ops

## 💡 Problem Description

Using comprehensive, daily-updated weather data for over 200 capital cities worldwide taken from [Kaggle](https://www.kaggle.com/datasets/nelgiriyewithana/global-weather-repository/data), the main goal of the project is to develop a machine learning model that forecasts the next-day weather conditions, including temperature, wind speed, precipitation, humidity, UV, gust, and air quality.

This project also presents a complete end-to-end ML Ops system, covering experiment tracking, a training pipeline, batch forecasting, monitoring, deployment and infrastructure provisioning.


## 🔧 Technical Stack

| Component | Technical Stack |
| -------- | ------- |
| Programming Language | Python 3.11 |
| Experiment Tracking | MLflow 2.1.1 |
| Model Registry | MLflow 2.1.1 |
| Orchestration | Dagster 1.11.2
| Monitoring | Grafana |
| Containerization | Docker, docker-compose
| CI/CD | Github Actions |
| IaC | Terraform |
| Database | AWS RDS (PostgreSQL 16.9) |
| Compute Engine | AWS EC2 |
| Cloud Storage | AWS S3 |
| Parameter Store | AWS SSM Parameter Store |
| Communication Platform | Slack |

## 🔬 Modeling
*Tracked and registered in MLflow*

### Features:
- country and city (encoded using LabelEncoder)
- latitude, longitude
- 30-day lag values of each target variable (e.g., temperature_celsius_lag_1, ..., temperature_celsius_lag_30)

### Target
```
temperature_celsius
temperature_fahrenheit
wind_mph
wind_kph
wind_degree
pressure_mb
pressure_in
precip_mm
precip_in
humidity
cloud
feels_like_celsius
feels_like_fahrenheit
visibility_km
visibility_miles
uv_index
gust_mph
gust_kph
air_quality_Carbon_Monoxide
air_quality_Ozone
air_quality_Nitrogen_dioxide
air_quality_Sulphur_dioxide
air_quality_PM2.5
air_quality_PM10
air_quality_us-epa-index
air_quality_gb-defra-index
```

### Training & Evaluation:
- Training data: 1 year of historical data, ranging from D−1 year 1 month to D−2 months
- Testing data: 1-month data from D−1 month
- Evaluation metrics: RMSE (Root Mean Squared Error) and NRMSE (Normalized RMSE)

### Model
- Using **Scikit-learn**’s MultiOutputRegressor and **XGBoost**

## ⚙️ Orchestration and Monitoring
*Developed using Dagster and Grafana*

### Data Ingestion
- Schedule: daily
- Ingest data from kaggle and store to PostgreSQL

### Automated Retraining Pipeline
- Schedule: monthly
- Every model is registered to MLflow model registry
- If the model's performance is better than the current production version, it will be promoted as the new production version

### Batch Forecasting
- Schedule: daily
- Input data: Last 30 days data

### Evaluation and monitoring
- Schedule: daily
- Process:
    - Comparing d-day prediction result with d-day actual data
    - Detect missing values
- Evaluation result will be monitored via grafana
- Any unusual data exceeded the defined threshold will be alerted to Slack

## 🛠️ How to Reproduce

### Prerequisite
- Have Python 3.11
- Have an AWS account
- Have `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (see: [AWS Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html))
- Have AWS CLI installed. Have logged in to AWS via CLI
- Have Terraform installed (see: [Hashicorp Guide](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli))
- Have docker and docker-compose installed (see: [Docker Guide](https://www.docker.com/get-started/))
- Have Slack space, Slack channel and Slack Webhook (see: [Slack Guide](https://api.slack.com/messaging/webhooks))
- Have pipenv installed

- Git clone repository
```
git clone https://github.com/sndryn/weather-forecast-mlops.git

cd weather-forecast-mlops
```
### Setup Infrastructure
- Create S3 bucket manually (via AWS CLI or console) for terraform state
- Setup some parameters in AWS Parameter Store (use `secure string`).
```
/mlops/db/instance_name
mlops/db/username
/mlops/db/password
/mlops/db/dagster_dbname
/mlops/db/weather_dbname
/mlops/db/mlflow_dbname

/mlops/mlflow/artifact_bucket
/mlops/mlflow/experiment_name
/mlops/mlflow/model_name

/mlops/slack/webhook
/mlops/slack/channel
/mlops/grafana/username
/mlops/grafana/password

```
- Fill out `prod.tfvars` with ssm parameter store paths
- Go to directory orchestrator
```
cd orchestrator
```
- Run terraform init
```
terraform init
```
- Run terraform plan
```
terraform plan -var-file=vars/prod.tfvars
```
- Run terraform apply
```
terraform apply -var-file=vars/prod.tfvars
```

### Run in Local Environment
- Run the following command
```
make all
```
- Connect to the following components via browser:
    - MLFlow: `localhost:5000`
    - Dagster: `localhost:3000`
    - Grafana: `localhost:5001`

### Deploy to Cloud via CLI
- SSH to EC2 Instance
```
```
- git clone
```
```
- Run the follow command
```
make all
```

## 📑 Index
- MLflow config
- Orchestrator
- Training Pipeline
- Batch Forecasting
- Evaluation
- Unit test
- Grafana config
- docker-compose.yml
- Makefile (including formatting: pylint, isort, black)
- pre-commit-config.yaml (including formatting: pylint, isort, black)
- Github actions
- IaC
