terraform {
    required_version = ">= 1.0"
    backend "s3" {
        bucket  = "tf-state-mlops-zoomcamp-stef"
        key     = "mlops.tfstate"
        region  = "ap-southeast-1"
        encrypt = true 
    }

}

provider "aws" {
    region = var.aws_region
}

