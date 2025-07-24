from typing import Tuple

import pandas as pd


def clean_up_country(df: pd.DataFrame) -> pd.DataFrame:
    # Written based on preprocess done by https://www.kaggle.com/code/cieldt/forecasting-weather
    country_corrections = {
        "كولومبيا": "Colombia",
        "火鸡": "Turkey",
        "USA United States of America": "United States of America",
        "Congo": "Democratic Republic of Congo",
        "Польша": "Poland",
        "Jemen": "Yemen",
        "Turkménistan": "Turkmenistan",
        "Polônia": "Poland",
        "Mexique": "Mexico",
        "Saint-Vincent-et-les-Grenadines": "Saint Vincent and the Grenadines",
        "Saudi Arabien": "Saudi Arabia",
        "Bélgica": "Belgium",
        "Südkorea": "South Korea",
        "Estonie": "Estonia",
        "Турция": "Turkey",
        "Гватемала": "Guatemala",
        "Inde": "India",
        "Komoren": "Comoros",
        "Malásia": "Malaysia",
        "Marrocos": "Morocco",
        "Letonia": "Latvia",
    }
    df["country"] = df["country"].apply(lambda x: country_corrections.get(x, x))
    return df


def preprocess_data(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df["last_updated_utc"] = pd.to_datetime(df["last_updated_epoch"], unit="s")
    df["day"] = df["last_updated_utc"].dt.day
    df["month"] = df["last_updated_utc"].dt.month

    dropped_columns = [
        "last_updated",
        "last_updated_epoch",
        "last_updated_utc",
        "sunrise",
        "sunset",
        "moonrise",
        "moonset",
        "wind_direction",
        "condition_text",
        "moon_phase",
        "moon_illumination",
        "timezone",
    ]

    df = df.drop(columns=dropped_columns)

    return df
