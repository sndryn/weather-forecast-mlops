module "s3-mlflow-artifact" {
    source        = "./modules/s3"
    bucket_name   = "${var.mlflow_artifact_bucket_name}"
}

module "sg" {
    source = "./modules/sg"
}

module "rds" {
    source = "./modules/rds"
    rds_engine_version              = "16.9"
    rds_instance_class              = "db.t3.micro" 
    rds_allocated_storage           = 20
    rds_db_username_ssm_name        = "/mlops/db/username"
    rds_db_password_ssm_name        = "/mlops/db/password"
    rds_publicly_accessible         = true

    rds_subnet_ids             = module.sg.subnet_ids
    rds_sg_id                  = module.sg.rds_sg_id
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