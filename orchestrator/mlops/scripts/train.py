import datetime
import os
import pickle
import warnings
from typing import List, Tuple

import mlflow
import mlflow.sklearn
import pandas as pd
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from sklearn.metrics import root_mean_squared_error
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor

from mlops.scripts.database import Database
from mlops.scripts.preprocess import preprocess_data

warnings.simplefilter(
    action="ignore", category=pd.errors.SettingWithCopyWarning
)

load_dotenv()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


def read_data(
    start_date: datetime.date, end_date: datetime.date
) -> pd.DataFrame:
    mlflow.log_param("soure_data_start_date", start_date)
    mlflow.log_param("soure_data_end_date", end_date)
    mlflow.log_param(
        "source_path", "nelgiriyewithana/global-weather-repository"
    )

    db = Database()
    df = db.read_weather_data(start_date, end_date)
    db.close()
    return df


def split_data(
    df: pd.DataFrame, start_date: datetime.date, end_date: datetime.date
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    border_date = start_date + relativedelta(months=12)

    mlflow.log_param("train_data_start_date", start_date)
    mlflow.log_param(
        "train_data_end_date", border_date - relativedelta(days=1)
    )
    mlflow.log_param("test_data_start_date", border_date)
    mlflow.log_param("test_data_end_date", end_date)

    train_df = df[
        (df["last_updated_date"] >= start_date)
        & (df["last_updated_date"] < border_date)
    ]
    test_df = df[
        (df["last_updated_date"] >= border_date)
        & (df["last_updated_date"] <= end_date)
    ]

    return train_df, test_df


def create_lag_columns(
    df: pd.DataFrame, target_cols: List[str], steps: int = 30
) -> pd.DataFrame:
    lagged_cols = []

    df = df.sort_values(
        by=["location_name", "country", "last_updated_date"]
    )
    for col in target_cols:
        for lag in range(1, steps + 1):
            lagged_col = df.groupby(["location_name", "country"])[
                col
            ].shift(lag)
            lagged_col.name = f"{col}_lag_{lag}"
            lagged_cols.append(lagged_col)

    df = pd.concat([df] + lagged_cols, axis=1)
    return df


def transform(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    categorical_cols: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    mlflow.log_param("encoder", "LabelEncoder")

    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        train_df[col] = le.fit_transform(train_df[col].astype(str))
        test_df[col] = le.transform(test_df[col].astype(str))
        encoders[col] = le

        filename = "encoder.pkl"
        with open(filename, "wb") as f:
            pickle.dump(encoders, f)

        mlflow.log_artifact(filename, artifact_path="label_encoder")
        os.remove(filename)

    return train_df, test_df


def evaluate(
    y_test: List, y_pred: List, target_cols: List[str]
) -> Tuple[List, float]:
    metrics_results = []
    all_nrmse = 0

    for i, col in enumerate(target_cols):
        rmse = root_mean_squared_error(y_test[col], y_pred[:, i])
        nrmse = rmse / (y_test[col].max() - y_test[col].min())

        metrics = {}
        metrics["target"] = col
        metrics["rmse"] = rmse
        metrics["nrmse"] = nrmse

        metrics_results.append(metrics)

        mlflow.log_metrics({f"rmse_{col}": rmse, f"nrmse_{col}": nrmse})
        all_nrmse += nrmse

    mean_nrmse = all_nrmse / len(target_cols)
    mlflow.log_metric("mean_nrmse", mean_nrmse)

    return metrics_results, mean_nrmse


def predict(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: List[str],
    target_cols: List[str],
):
    x_train = train_df[feature_cols]
    x_test = test_df[feature_cols]
    y_train = train_df[target_cols]
    y_test = test_df[target_cols]

    n_estimators = 1
    random_state = 42
    n_jobs = -1

    mlflow.set_tag("model", "sklearn")
    mlflow.set_tag("model", "MultiOutputRegressor")
    mlflow.set_tag("model", "XGBRegressor")
    mlflow.log_param("n_esimator", 100)
    mlflow.log_param("random_state", 42)
    mlflow.log_param("n_job", -1)

    model = MultiOutputRegressor(
        XGBRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=n_jobs,
        )
    )
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)

    _, _ = evaluate(y_test, y_pred, target_cols)

    mlflow.sklearn.log_model(model, artifact_path="model")


def run(start_date: datetime.date, end_date: datetime.date):
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    mlflow.set_tag("created_by", "AUTOMATIC-TRAINING-PIPELINE")

    df = read_data(start_date, end_date)

    categorical_cols = ["country", "location_name"]
    numerical_cols = ["latitude", "longitude", "day", "month"]
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

    df = preprocess_data(df)
    df = create_lag_columns(df, target_cols)
    train_df, test_df = split_data(df, start_date, end_date)

    lag_features = [col for col in train_df.columns if "_lag_" in col]
    feature_cols = lag_features + categorical_cols + numerical_cols
    train_df, test_df = transform(train_df, test_df, categorical_cols)
    predict(train_df, test_df, feature_cols, target_cols)
