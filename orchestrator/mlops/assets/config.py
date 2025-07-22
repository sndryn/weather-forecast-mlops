from datetime import datetime, timedelta

from dagster import Config


class AssetConfig(Config):
    yesterday_date: str = (datetime.now() - timedelta(1)).strftime(
        "%Y-%m-%d"
    )
    today_date: str = (datetime.now()).strftime("%Y-%m-%d")
    tomorrow_date: str = (datetime.now() + timedelta(1)).strftime(
        "%Y-%m-%d"
    )
