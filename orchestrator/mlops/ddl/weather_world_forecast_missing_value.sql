CREATE TABLE IF NOT EXISTS weather_world_forecast_missing_value (
    missing_location_name       text[],
    number_of_missing_value     int,
    prediction_date             DATE,
    _load_timestamp             TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_global_weather_last_updated ON weather_world_forecast_missing_value(prediction_date);
