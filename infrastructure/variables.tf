variable "aws_region" {
    description = "AWS region to create resources"
    default     = "ap-southeast-1"
}

variable "mlflow_artifact_bucket_name" {
    description = "MLFlow artifact bucket names"
}

variable "rds_instance_identifier" {
    description = "RDS instance identifier"
}

# variable "vpc_id" {}
# variable "whitelisted_ip" {}