from datetime import datetime

from dagster import ScheduleDefinition, asset, define_asset_job
from dateutil.relativedelta import relativedelta

from mlops.assets.config import AssetConfig
from mlops.scripts import register_model, train

DAG_GROUP_NAME = "training"


@asset(
    key="weather_data_training",
    group_name=DAG_GROUP_NAME,
    compute_kind="pandas",
    deps=["weather_data_trainging"],
)
def asset_train_weather_data(config: AssetConfig):
    config_date = datetime.strptime(
        config.yesterday_date, "%Y-%m-%d"
    ).date()
    start_date = (config_date - relativedelta(years=1)).replace(day=1)
    end_date = config_date

    train.run(start_date, end_date)


@asset(
    key="register_weather_model",
    group_name=DAG_GROUP_NAME,
    compute_kind="pandas",
    deps=["weather_data_training"],
)
def asset_register_model():
    run = register_model.search_latest_run()
    (
        model_version,
        mean_nrmse,
    ) = register_model.register(run)
    register_model.promote_to_prod(model_version, mean_nrmse)


schedule = ScheduleDefinition(
    job=define_asset_job(
        f"{DAG_GROUP_NAME}_job",
        selection=[
            asset_train_weather_data,
            asset_register_model,
        ],
    ),
    cron_schedule="0 15 1 * *",
    execution_timezone="UTC",
)
