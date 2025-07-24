from unittest.mock import MagicMock

import pandas as pd
from sklearn.preprocessing import LabelEncoder

from mlops.scripts.forecast import create_lag_columns, predict, transform


def test_create_lag_columns():
    data = {
        "location_name": ["loc1"] * 3,
        "country": ["country1"] * 3,
        "last_updated_date": pd.to_datetime(
            [
                "2023-01-01",
                "2023-01-02",
                "2023-01-03",
            ]
        ),
        "temperature_celsius": [10, 12, 14],
        "wind_mph": [5, 7, 6],
    }
    df = pd.DataFrame(data)

    feature_cols = ["location_name", "country"]
    target_cols = [
        "temperature_celsius",
        "wind_mph",
    ]

    lagged_df = create_lag_columns(df, feature_cols, target_cols, steps=3)

    expected_cols = feature_cols + [
        "temperature_celsius_lag_1",
        "temperature_celsius_lag_2",
        "temperature_celsius_lag_3",
        "wind_mph_lag_1",
        "wind_mph_lag_2",
        "wind_mph_lag_3",
    ]
    assert all(col in lagged_df.columns for col in expected_cols)

    assert lagged_df.loc[0, "temperature_celsius_lag_1"] == 14
    assert lagged_df.loc[0, "wind_mph_lag_3"] == 5


def test_transform():
    data = {
        "country": ["USA", "Canada", "USA"],
        "location_name": ["loc1", "loc2", "loc1"],
    }
    df = pd.DataFrame(data)
    encoders = {
        "country": LabelEncoder().fit(["USA", "Canada"]),
        "location_name": LabelEncoder().fit(["loc1", "loc2"]),
    }
    transformed_df = transform(df, ["country", "location_name"], encoders)

    assert transformed_df["country"].dtype.kind in (
        "i",
        "u",
    )
    assert transformed_df["location_name"].dtype.kind in (
        "i",
        "u",
    )


def test_predict():
    df = pd.DataFrame(
        {
            "country": [1, 2],
            "latitude": [3, 4],
        }
    )
    feature_cols = ["country", "latitude"]
    target_cols = [
        "temperature_celsius",
        "wind_mph",
    ]

    model = MagicMock()
    model.predict.return_value = [
        [0.5, 1.5],
        [2.5, 3.5],
    ]

    preds_df = predict(df, feature_cols, target_cols, model)

    assert list(preds_df.columns) == target_cols
    assert preds_df.iloc[0, 0] == 0.5
