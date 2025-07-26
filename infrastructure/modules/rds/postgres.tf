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
  connect_timeout = 60
}

data "aws_ssm_parameter" "mlflow_db_name" {
    name            = var.postgres_ssm_mlflow_db_name
    with_decryption = true
}

data "aws_ssm_parameter" "dagster_db_name" {
    name            = var.postgres_ssm_dagster_db_name
    with_decryption = true
}

data "aws_ssm_parameter" "weather_db_name" {
    name            = var.postgres_ssm_weather_db_name
    with_decryption = true
}

resource "postgresql_database" "mlflow" {
  name        = data.aws_ssm_parameter.mlflow_db_name.value
  depends_on  = [aws_db_instance.mlops_db]
}

resource "postgresql_database" "dagster" {
  name        = data.aws_ssm_parameter.dagster_db_name.value
  depends_on  = [aws_db_instance.mlops_db]
}

resource "postgresql_database" "weather_forecast" {
  name        = data.aws_ssm_parameter.weather_db_name.value
  depends_on  = [aws_db_instance.mlops_db]
}
