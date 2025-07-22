
data "aws_ssm_parameter" "s3_bucket_name" {
    name            = var.s3_bucket_ssm_name
    with_decryption = true
}

resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = data.aws_ssm_parameter.s3_bucket_name.value.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "name" {
    value = aws_s3_bucket.s3_bucket.bucket
}
