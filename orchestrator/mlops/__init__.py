from dagster import Definitions, load_assets_from_modules

from mlops.assets import batch_forecasting, ingestion, training

all_assets = load_assets_from_modules(
    [ingestion, training, batch_forecasting]
)

all_schedules = [
    ingestion.schedule,
    training.schedule,
    batch_forecasting.schedule,
]

defs = Definitions(
    assets=all_assets,
    schedules=all_schedules,
)
