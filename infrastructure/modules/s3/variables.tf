variable "s3_bucket_ssm_name" {
    description = "SSM parameter name containing S3 bucket name"
    type        = string
    default     = "/mlops/s3/bucket_name"
}
