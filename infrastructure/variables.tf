variable "aws_region" {
    description = "AWS region to create resources"
    default     = "ap-southeast-1"
}

variable "ssm_artifact_bucket" {
    description = "MLFlow artifact bucket names"
}

variable "ssm_db_instance_name" {
    description = "SSM parameter name containing DB Instance name"
}

variable "ssm_db_username" {
    description = "SSM parameter name containing DB username"
}

variable "ssm_db_password" {
    description = "SSM parameter name containing DB username"
}

variable "ssm_dagster_db_name" {
    type = string
}

variable "ssm_mlflow_db_name" {
    type = string
}

variable "ssm_weather_db_name" {
    type = string
}

variable "ssm_instance_key_name" {
    type = string
}

# variable "vpc_id" {}
# variable "whitelisted_ip" {}
