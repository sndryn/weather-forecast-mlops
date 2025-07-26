import pandas as pd

from mlops.scripts.preprocess import clean_up_country, preprocess_data


def test_clean_up_country():
    data = {
        "country": [
            "كولومبيا",
            "火鸡",
            "USA United States of America",
            "Germany",
        ]
    }
    df = pd.DataFrame(data)

    cleaned_df = clean_up_country(df)

    expected = [
        "Colombia",
        "Turkey",
        "United States of America",
        "Germany",
    ]
    assert cleaned_df["country"].tolist() == expected


def test_preprocess_data():
    # Input with necessary columns
    data = {
        "last_updated_epoch": [1721088000],
        "last_updated": ["2024-07-16 00:00"],
        "sunrise": ["6:00 AM"],
        "sunset": ["7:00 PM"],
        "moonrise": ["9:00 PM"],
        "moonset": ["5:00 AM"],
        "wind_direction": ["NW"],
        "condition_text": ["Clear"],
        "moon_phase": ["Waxing Gibbous"],
        "moon_illumination": [82],
        "timezone": ["UTC"],
    }

    df = pd.DataFrame(data)

    processed_df = preprocess_data(df.copy())

    dropped = [
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
    for col in dropped:
        assert col not in processed_df.columns

    assert "day" in processed_df.columns
    assert "month" in processed_df.columns
    assert processed_df["day"].iloc[0] == 16
    assert processed_df["month"].iloc[0] == 7
