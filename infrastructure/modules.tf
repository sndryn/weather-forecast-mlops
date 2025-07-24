module "s3-mlflow-artifact" {
    source                  = "./modules/s3"
    s3_ssm_artifact_bucket  = var.ssm_artifact_bucket
}

module "sg" {
    source = "./modules/sg"
}

module "rds" {
    source = "./modules/rds"
    rds_engine_version              = "16.9"
    rds_instance_class              = "db.t3.micro"
    rds_allocated_storage           = 20
    rds_ssm_db_instance_name        = var.ssm_db_instance_name
    rds_ssm_db_username             = var.ssm_db_username
    rds_ssm_db_password             = var.ssm_db_password

    rds_subnet_ids                  = module.sg.subnet_ids
    rds_sg_id                       = module.sg.rds_sg_id

    postgres_ssm_mlflow_db_name     = var.ssm_mlflow_db_name
    postgres_ssm_dagster_db_name    = var.ssm_dagster_db_name
    postgres_ssm_weather_db_name    = var.ssm_weather_db_name
}

module "iam" {
  source = "./modules/iam"
}

# module "ec2" {
#   source                    = "./modules/ec2"
#   subnet_id                 = var.public_subnet_id
#   key_name                  = var.key_pair_name
#   security_group_id         = module.security_groups.ec2_sg_id
#   iam_instance_profile_name = module.iam.instance_profile_name
# }
