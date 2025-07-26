data "aws_ssm_parameter" "rds_db_instance_mame" {
    name            = var.rds_ssm_db_instance_name
    with_decryption = true
}

data "aws_ssm_parameter" "rds_db_username" {
    name            = var.rds_ssm_db_username
    with_decryption = true
}

data "aws_ssm_parameter" "rds_db_password" {
    name            = var.rds_ssm_db_password
    with_decryption = true
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "${data.aws_ssm_parameter.rds_db_instance_mame.value}-subnet-group"
  subnet_ids = var.rds_subnet_ids

  tags = {
    name  = "mlops-db-subnet-group"
  }
}

resource "aws_db_instance" "mlops_db" {
    identifier                  = data.aws_ssm_parameter.rds_db_instance_mame.value
    engine                      = "postgres"
    engine_version              = var.rds_engine_version
    instance_class              = var.rds_instance_class
    allocated_storage           = var.rds_allocated_storage
    storage_type                = "gp3"
    username                    = data.aws_ssm_parameter.rds_db_username.value
    password                    = data.aws_ssm_parameter.rds_db_password.value
    port                        = 5432
    publicly_accessible         = var.rds_publicly_accessible
    skip_final_snapshot         = true
    backup_retention_period     = 7
    auto_minor_version_upgrade  = true
    db_subnet_group_name        = aws_db_subnet_group.rds_subnet_group.name
    vpc_security_group_ids      = [var.rds_sg_id]

  tags = {
    Name = "mlops-db-instance"
  }
}

output "endpoint" {
  description = "RDS endpoint address"
  value       = aws_db_instance.mlops_db.endpoint
}

output "port" {
  description = "RDS port"
  value       = aws_db_instance.mlops_db.port
}
