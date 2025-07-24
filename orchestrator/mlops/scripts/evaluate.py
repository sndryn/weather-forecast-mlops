import datetime
from typing import Tuple

import pandas as pd
from sklearn.metrics import root_mean_squared_error

from mlops.scripts.database import Database


def read_data(
    date: datetime.date,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    db = Database()
    actual_df = db.read_weather_data(start_date=date, end_date=date)

    query = f"""
        SELECT * FROM weather_world_forecast
        WHERE prediction_date = '{date}'
    """
    prediction_df = pd.read_sql(query, con=db.engine)

    db.close()
    return actual_df, prediction_df


def store(
    df: pd.DataFrame,
    prediction_date: datetime.date,
    table_name: str,
):
    db = Database()
    if not db.check_if_table_exist(table_name):
        ddl = open(f"mlops/ddl/{table_name}.sql", "r", encoding="utf-8").read()
        db.execute(ddl)

    db.execute(
        f"DELETE FROM {table_name} WHERE prediction_date = '{prediction_date}'"
    )
    df.to_sql(
        table_name,
        con=db.engine,
        if_exists="append",
        index=False,
    )
    db.close()


def get_missing_locations(
    actual_df: pd.DataFrame,
    prediction_df: pd.DataFrame,
    prediction_date: datetime.date,
) -> pd.DataFrame:
    missing_value = list(
        set(actual_df["location_name"])
        - set(prediction_df["location_name"].tolist())
    )
    print(missing_value)
    missing_df = pd.DataFrame(
        [
            {
                "missing_location_name": missing_value,
                "number_of_missing_value": len(missing_value),
                "prediction_date": prediction_date,
                "_load_timestamp": datetime.datetime.now(),
            }
        ]
    )
    return missing_df


def get_evaluation_metrics(
    actual_df: pd.DataFrame,
    prediction_df: pd.DataFrame,
    prediction_date: datetime.date,
) -> pd.DataFrame:
    combined_df = actual_df.merge(
        prediction_df,
        how="left",
        on=["country", "location_name"],
        suffixes=("_actual", "_pred"),
    )
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

    metrics_results = []
    all_nrmse = 0

    for _, col in enumerate(target_cols):
        rmse = root_mean_squared_error(
            combined_df[col + "_actual"],
            combined_df[col + "_pred"],
        )
        nrmse = rmse / (
            combined_df[col + "_actual"].max()
            - combined_df[col + "_actual"].min()
        )

        metrics = {}
        metrics["target_name"] = col
        metrics["rmse"] = rmse
        metrics["nrmse"] = nrmse

        metrics_results.append(metrics)
        all_nrmse += nrmse

    mean_nrmse = all_nrmse / len(target_cols)
    metrics_results.append(
        {
            "target_name": "overall",
            "rmse": None,
            "nrmse": mean_nrmse,
        }
    )
    metrics_df = pd.DataFrame(metrics_results)
    metrics_df["prediction_date"] = prediction_date
    metrics_df["_load_timestamp"] = datetime.datetime.now()
    return metrics_df


def run(date: datetime.date):
    actual_df, prediction_df = read_data(date)

    missing_df = get_missing_locations(
        actual_df, prediction_df, prediction_date=date
    )
    store(
        missing_df,
        date,
        "weather_world_forecast_missing_value",
    )

    metrics_df = get_evaluation_metrics(
        actual_df, prediction_df, prediction_date=date
    )
    store(metrics_df, date, "weather_world_forecast_metrics")
