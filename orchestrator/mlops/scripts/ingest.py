import shutil
from datetime import date, datetime

import kagglehub
import pandas as pd

from mlops.scripts.database import Database
from mlops.scripts.preprocess import clean_up_country

TABLE_NAME = "weather_world"


def ingest_from_kaggle():
    kaggle_path = "nelgiriyewithana/global-weather-repository"
    file_path = "GlobalWeatherRepository.csv"

    local_path = kagglehub.dataset_download(kaggle_path)
    df = pd.read_csv(f"{local_path}/{file_path}")

    df["last_updated_utc"] = pd.to_datetime(
        df["last_updated_epoch"], unit="s"
    )
    df["last_updated_date"] = df["last_updated_utc"].dt.date
    df["_load_timestamp"] = datetime.now()
    df = df.drop(columns=["last_updated_utc"])

    df = clean_up_country(df)
    df.columns = df.columns.str.lower().str.replace("-", "_")
    df.columns = df.columns.str.replace("pm2.5", "pm2_5")
    print(df.columns)

    shutil.rmtree(local_path)
    return df


def ingest_into_db(df: pd.DataFrame, year: int, month: int, day: int):
    db = Database()
    if db.check_if_table_exist(TABLE_NAME):
        result_df = df[
            df["last_updated_date"] == date(year, month, day)
        ]
        db.execute(
            f"DELETE FROM {TABLE_NAME} WHERE last_updated_date = '{year}-{month:02d}-{day:02d}'"
        )
    else:
        ddl = open(
            "mlops/ddl/weather_world.sql", "r", encoding="utf-8"
        ).read()
        db.execute(ddl)
        result_df = df

    result_df.to_sql(
        name=TABLE_NAME,
        con=db.engine,
        if_exists="append",
        index=False,
        chunksize=1000,
    )
    db.close()
