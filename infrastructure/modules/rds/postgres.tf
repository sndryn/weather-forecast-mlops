terraform {
  required_providers {
    postgresql = {
      source  = "cyrilgdn/postgresql"
    }
  }

  required_version = ">= 1.0.0"
}

provider "postgresql" {
  host            = aws_db_instance.mlops_db.address
  port            = aws_db_instance.mlops_db.port
  username        = data.aws_ssm_parameter.rds_db_username.value
  password        = data.aws_ssm_parameter.rds_db_password.value
  database        = "postgres"
  sslmode         = "require"
  connect_timeout = 15
}

resource "postgresql_database" "mlflow" {
  name = var.postgres_ssm_mlflow_db_name
}

resource "postgresql_database" "dagster" {
  name = var.postgres_ssm_dagster_db_name
}

resource "postgresql_database" "weather_forecast" {
  name = var.postgres_ssm_weather_db_name
}
