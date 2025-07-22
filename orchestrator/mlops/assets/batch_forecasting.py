from datetime import datetime

from dagster import ScheduleDefinition, asset, define_asset_job

from mlops.assets.config import AssetConfig
from mlops.scripts import evaluate, forecast

DAG_GROUP_NAME = "batch_forecasting"


@asset(
    key="weather_data_forecasting",
    group_name=DAG_GROUP_NAME,
    compute_kind="pandas",
    deps=["weather_data_ingestion"],
)
def asset_forecast_weather(config: AssetConfig):
    today_date = datetime.strptime(config.today_date, "%Y-%m-%d").date()
    tomorrow_date = datetime.strptime(
        config.tomorrow_date, "%Y-%m-%d"
    ).date()

    forecast.run(today_date, tomorrow_date)


@asset(
    key="weather_data_forecast_evaluation",
    group_name=DAG_GROUP_NAME,
    compute_kind="pandas",
    deps=["weather_data_forecasting"],
)
def asset_evaluate_forecast_weather(
    config: AssetConfig,
):
    today_date = datetime.strptime(config.today_date, "%Y-%m-%d").date()
    evaluate.run(today_date)


schedule = ScheduleDefinition(
    job=define_asset_job(
        f"{DAG_GROUP_NAME}_job",
        selection=[
            asset_forecast_weather,
            asset_evaluate_forecast_weather,
        ],
    ),
    cron_schedule="0 15 * * *",
    execution_timezone="UTC",
)
