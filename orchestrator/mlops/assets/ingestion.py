from datetime import datetime

from dagster import ScheduleDefinition, asset, define_asset_job

from mlops.assets.config import AssetConfig
from mlops.scripts.ingest import ingest_from_kaggle, ingest_into_db

DAG_GROUP_NAME = "ingestion"


@asset(
    key="weather_data_ingestion",
    group_name=DAG_GROUP_NAME,
    compute_kind="pandas",
)
def asset_ingest_weather_data(
    config: AssetConfig,
):
    date = datetime.strptime(config.today_date, "%Y-%m-%d")

    df = ingest_from_kaggle()
    ingest_into_db(df, date.year, date.month, date.day)


schedule = ScheduleDefinition(
    job=define_asset_job(
        f"{DAG_GROUP_NAME}_job",
        selection=[asset_ingest_weather_data],
    ),
    cron_schedule="0 15 * * *",
    execution_timezone="UTC",
)
