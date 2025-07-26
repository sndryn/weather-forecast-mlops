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
    rds_publicly_accessible         = true
}

module "iam" {
  source                  = "./modules/iam"
  s3_ssm_artifact_bucket  = var.ssm_artifact_bucket
}

module "ec2" {
    source                  = "./modules/ec2"
    ec2_subnet_id           = module.sg.subnet_ids[0]
    ec2_sg_id               = module.sg.ec2_sg_id
    ssm_instance_key_name   = var.ssm_instance_key_name
    ec2_profile             = module.iam.instance_profile_name
}
