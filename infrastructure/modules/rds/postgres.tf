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
  name = "mlflow"
}

resource "postgresql_database" "dagster" {
  name = "dagster"
}

resource "postgresql_database" "weather_forecast" {
  name = "weather_forecast"
}


# resource "postgresql_role" "mlops_user" {
#   name     = data.aws_ssm_parameter.rds_db_username.value
#   password = data.aws_ssm_parameter.rds_db_password.value
#   login    = true
# }

# resource "postgresql_grant" "mlflow_db_access" {
#   database   = postgresql_database.mlflow.name
#   role       = postgresql_role.mlops_user.name
#   privileges = ["CONNECT"]
# }

# resource "postgresql_grant" "dagster_db_access" {
#   database   = postgresql_database.dagster.name
#   role       = postgresql_role.mlops_user.name
#   privileges = ["CONNECT"]
# }

# resource "postgresql_grant" "weather_db_access" {
#   database   = postgresql_database.weather_forecast.name
#   role       = postgresql_role.mlops_user.name
#   privileges = ["CONNECT"]
# }
