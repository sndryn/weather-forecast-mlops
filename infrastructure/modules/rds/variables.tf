variable "rds_db_instance_ssm_name" {
    description = "SSM parameter name containing DB Instance name"
    type        = string
    default     = "/mlops/db/instance_name"
}

variable "rds_db_username_ssm_name" {
    description = "SSM parameter name containing DB username"
    type        = string
    default     = "/mlops/db/username"
}

variable "rds_db_password_ssm_name" {
    description = "SSM parameter name containing DB username"
    type        = string
    default     = "/mlops/db/password"
}

variable "rds_instance_class" {
    description = "RDS instance class"
    type        = string
    default     = "db.t3.micro" 
}

variable "rds_allocated_storage" {
    description = "Allocated storage in GB"
    type        = number
    default     = 20
}

variable "rds_publicly_accessible" {
    description = "Whether the DB is publicly accessible"
    type        = bool
    default     = false
}

variable "rds_engine_version" {
    description = "Postgres engine version"
    type        = string
    default     = "16.9"
}

variable "rds_sg_id" {
}

variable "rds_subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for the RDS subnet group"
}
