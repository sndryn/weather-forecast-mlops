import datetime
import os
import pickle
import tempfile
from typing import List, Tuple

import mlflow
import pandas as pd
import sklearn
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from mlflow.tracking import MlflowClient

from mlops.scripts.database import Database

load_dotenv()


MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME")
MLFLOW_MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient()


def get_model() -> (
    Tuple[sklearn.multioutput.MultiOutputRegressor, dict]
):
    versions = client.search_model_versions(
        f"name='{MLFLOW_MODEL_NAME}'"
    )

    versions = sorted(
        versions, key=lambda v: int(v.version), reverse=True
    )
    model_uri = ""
    for v in versions:
        env = v.tags.get("environment")
        if env != "production":
            continue
        run_id = v.run_id
        model_uri = f"runs:/{run_id}/model"
        model = mlflow.sklearn.load_model(model_uri)

        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = mlflow.artifacts.download_artifacts(
                run_id=run_id,
                artifact_path="label_encoder/encoder.pkl",
                dst_path=tmpdir,
            )
            with open(local_path, "rb") as f:
                encoder = pickle.load(f)
        return model_uri, model, encoder


def read_data(
    start_date: datetime.date, end_date: datetime.date
) -> pd.DataFrame:
    db = Database()
    df = db.read_weather_data(start_date, end_date)
    db.close()
    return df


def create_lag_columns(
    df: pd.DataFrame,
    feature_cols: list,
    target_cols: list,
    steps: int = 30,
) -> pd.DataFrame:
    df_sorted = df.sort_values(
        feature_cols + ["last_updated_date"],
        ascending=[True] * (len(feature_cols)) + [False],
    )
    grouped = (
        df_sorted.groupby(feature_cols)[target_cols]
        .agg(list)
        .reset_index()
    )

    lagged_dfs = []
    for col in target_cols:
        lag_cols = pd.DataFrame(
            grouped[col].tolist(),
            columns=[f"{col}_lag_{i+1}" for i in range(steps)],
        )
        lagged_dfs.append(lag_cols)

    result = pd.concat([grouped[feature_cols]] + lagged_dfs, axis=1)
    return result


def transform(df: pd.DataFrame, categorical_cols: List[str], encoders):
    test_df = df.copy()
    for col in categorical_cols:
        le = encoders[col]
        test_df[col] = le.transform(test_df[col].astype(str))

    return test_df


def predict(
    df: pd.DataFrame,
    feature_cols: List[str],
    target_cols: List[str],
    model,
):
    x = df[feature_cols]

    predictions = model.predict(x)
    preds_df = pd.DataFrame(
        predictions, columns=target_cols, index=df.index
    )
    return preds_df


def store(df: pd.DataFrame, prediction_date: datetime.date):
    table_name = "weather_world_forecast"

    db = Database()
    if not db.check_if_table_exist(table_name):
        ddl = open(
            "mlops/ddl/weather_world_forecast.sql",
            "r",
            encoding="utf-8",
        ).read()
        db.execute(ddl)

    db.execute(
        f"DELETE FROM {table_name} WHERE prediction_date = '{prediction_date}'"
    )
    df.to_sql(
        table_name, con=db.engine, if_exists="append", index=False
    )
    db.close()


def run(
    config_date: datetime.date,
    prediction_date: datetime.date,
    steps: int = 30,
):
    end_date = config_date
    start_date = config_date - relativedelta(days=steps - 1)

    df = read_data(start_date, end_date)

    categorical_cols = ["country", "location_name"]
    numerical_cols = ["latitude", "longitude"]
    date_cols = ["day", "month"]
    target_cols = [
        "temperature_celsius",
        "temperature_fahrenheit",
        "wind_mph",
        "wind_kph",
        "wind_degree",
        "pressure_mb",
        "pressure_in",
        "precip_mm",
        "precip_in",
        "humidity",
        "cloud",
        "feels_like_celsius",
        "feels_like_fahrenheit",
        "visibility_km",
        "visibility_miles",
        "uv_index",
        "gust_mph",
        "gust_kph",
        "air_quality_carbon_monoxide",
        "air_quality_ozone",
        "air_quality_nitrogen_dioxide",
        "air_quality_sulphur_dioxide",
        "air_quality_pm2_5",
        "air_quality_pm10",
        "air_quality_us_epa_index",
        "air_quality_gb_defra_index",
    ]

    df = create_lag_columns(
        df, categorical_cols + numerical_cols, target_cols
    )
    df["day"] = prediction_date.day
    df["month"] = prediction_date.month

    model_uri, model, encoders = get_model()

    lag_features = [col for col in df.columns if "_lag_" in col]
    feature_cols = (
        lag_features + categorical_cols + numerical_cols + date_cols
    )
    test_df = transform(df, categorical_cols, encoders)
    pred_df = predict(test_df, feature_cols, target_cols, model)
    pred_df = pd.concat([df, pred_df], axis=1)
    pred_df = pred_df.drop(columns=lag_features + date_cols)
    pred_df["prediction_date"] = prediction_date
    pred_df["model_uri"] = model_uri
    pred_df["_load_timestamp"] = datetime.datetime.now()

    store(pred_df, prediction_date=prediction_date)
