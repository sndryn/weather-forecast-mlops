CREATE TABLE IF NOT EXISTS weather_world_forecast_metrics (
    target_name             VARCHAR(100),
    rmse                    FLOAT,
    nrmse                   FLOAT,
    prediction_date         DATE,
    _load_timestamp         TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_global_weather_last_updated ON weather_world_forecast_metrics(prediction_date);
