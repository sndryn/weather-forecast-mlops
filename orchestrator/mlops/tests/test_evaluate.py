import datetime

import pandas as pd

from mlops.scripts.evaluate import get_missing_locations


def test_get_missing_locations():
    actual_df = pd.DataFrame(
        {
            "location_name": [
                "Loc1",
                "Loc2",
                "Loc3",
            ]
        }
    )
    prediction_df = pd.DataFrame({"location_name": ["Loc2", "Loc4"]})
    prediction_date = datetime.date(2025, 7, 22)

    result = get_missing_locations(
        actual_df, prediction_df, prediction_date
    )

    assert "missing_location_name" in result.columns
    assert "number_of_missing_value" in result.columns
    assert "prediction_date" in result.columns
    assert "_load_timestamp" in result.columns

    assert set(result.loc[0, "missing_location_name"]) == {
        "Loc1",
        "Loc3",
    }
    assert result.loc[0, "number_of_missing_value"] == 2
    assert result.loc[0, "prediction_date"] == prediction_date
