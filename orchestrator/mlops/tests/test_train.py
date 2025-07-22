import pandas as pd
import pytest

from mlops.scripts.train import create_lag_columns


@pytest.fixture
def mock_df():
    dates = pd.date_range(start="2024-01-01", periods=31)
    data = []
    for location in ["LocationA", "LocationB"]:
        for date in dates:
            data.append(
                {
                    "location_name": location,
                    "country": "CountryX",
                    "last_updated_date": date.date(),
                    "temperature_celsius": 20.0,
                    "latitude": 1.1,
                    "longitude": 2.2,
                    "day": date.day,
                    "month": date.month,
                }
            )
    df = pd.DataFrame(data)
    return df


def test_create_lag_columns(mock_df):
    target_cols = ["temperature_celsius"]
    lagged_df = create_lag_columns(mock_df, target_cols)

    for i in range(1, 31):
        assert f"temperature_celsius_lag_{i}" in lagged_df.columns

    grouped = lagged_df.groupby(["location_name", "country"])
    for _, group in grouped:
        assert (
            group.iloc[0]["temperature_celsius_lag_1"]
            != group.iloc[0]["temperature_celsius"]
        )
