data "aws_ssm_parameter" "ssm_s3_artifact_bucket" {
    name            = var.s3_ssm_artifact_bucket
    with_decryption = true
}

resource "aws_s3_bucket" "s3_bucket" {
    bucket  = data.aws_ssm_parameter.ssm_s3_artifact_bucket.value
}

resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.s3_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "name" {
    value = aws_s3_bucket.s3_bucket.bucket
}
