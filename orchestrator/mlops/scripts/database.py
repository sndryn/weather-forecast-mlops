import os
from datetime import date

import pandas as pd
import psycopg
from sqlalchemy import create_engine


class Database:
    def __init__(self):
        self.host = os.getenv("WEATHER_DB_HOSTNAME")
        self.username = os.getenv("WEATHER_DB_USERNAME")
        self.password = os.getenv("WEATHER_DB_PASSWORD")
        self.db_name = os.getenv("WEATHER_DB_NAME")
        self.port = 5432

        conn_str = (
            f"host={self.host} "
            f"port={self.port} "
            f"user={self.username} "
            f"password={self.password} "
            f"dbname={self.db_name}"
        )
        self.conn = psycopg.connect(
            conn_str,
            autocommit=True,
        )

        self.connection_string = (
            f"postgresql+psycopg2://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.db_name}"
        )

        self.engine = create_engine(self.connection_string)

    def check_if_table_exist(self, table_name: str) -> bool:
        res = self.conn.execute(
            """
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = %s
            """,
            (table_name,),
        )
        return len(res.fetchall()) != 0

    def execute(self, query: str):
        self.conn.execute(query)

    def read_weather_data(
        self, start_date: date, end_date: date
    ) -> pd.DataFrame:
        query = f"""
            SELECT * FROM weather_world
            WHERE last_updated_date BETWEEN '{start_date}' AND '{end_date}'
        """
        df = pd.read_sql(query, con=self.engine)
        return df

    def close(self):
        self.conn.close()
