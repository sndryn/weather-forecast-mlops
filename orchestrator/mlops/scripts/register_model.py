import os
from typing import Tuple

import mlflow
from dotenv import load_dotenv
from mlflow.tracking import MlflowClient

load_dotenv()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME")
MLFLOW_MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient()


def search_latest_run() -> mlflow.run:
    experiment = client.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
    filter_string = 'tags.created_by = "AUTOMATIC-TRAINING-PIPELINE"'

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=filter_string,
        order_by=["attributes.start_time DESC"],
        max_results=1,
    )

    run = runs[0]
    return run


def register(run: mlflow.run) -> Tuple[int, float]:
    run_id = run.info.run_id
    model_uri = f"runs:/{run_id}/model"
    mean_nrmse = run.data.metrics.get("mean_nrmse")

    try:
        client.create_registered_model(MLFLOW_MODEL_NAME)
    except Exception:
        pass

    model_version = client.create_model_version(
        name=MLFLOW_MODEL_NAME,
        source=model_uri,
        run_id=run_id,
    )
    client.set_model_version_tag(
        name=MLFLOW_MODEL_NAME,
        version=model_version.version,
        key="mean_nrmse",
        value=str(mean_nrmse),
    )
    client.set_model_version_tag(
        name=MLFLOW_MODEL_NAME,
        version=model_version.version,
        key="environment",
        value="development",
    )
    return model_version.version, mean_nrmse


def promote_to_prod(model_version: int, mean_nrmse: float):
    versions = client.search_model_versions(
        f"name='{MLFLOW_MODEL_NAME}'"
    )
    prod_versions = [
        v for v in versions if v.tags.get("environment") == "production"
    ]
    print(prod_versions)

    if len(prod_versions) == 0:
        client.set_model_version_tag(
            name=MLFLOW_MODEL_NAME,
            version=model_version,
            key="environment",
            value="production",
        )

    for v in prod_versions:
        prod_mean_nrmse = float(v.tags.get("mean_nrmse", float("inf")))
        if (
            int(v.version) != model_version
            and float(mean_nrmse) >= prod_mean_nrmse
        ):
            client.set_model_version_tag(
                name=MLFLOW_MODEL_NAME,
                version=v.version,
                key="environment",
                value="archived",
            )
            client.set_model_version_tag(
                name=MLFLOW_MODEL_NAME,
                version=model_version,
                key="environment",
                value="production",
            )
