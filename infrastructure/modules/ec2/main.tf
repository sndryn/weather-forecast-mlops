data "aws_ssm_parameter" "ssm_instance_key_name" {
    name            = var.ssm_instance_key_name
    with_decryption = true
}

resource "aws_instance" "mlops" {
    ami                         = var.ec2_ami
    instance_type               = var.ec2_instance_type
    subnet_id                   = var.ec2_subnet_id
    vpc_security_group_ids      = [var.ec2_sg_id]
    key_name                    = data.aws_ssm_parameter.ssm_instance_key_name.value
    associate_public_ip_address = true
    iam_instance_profile        = var.ec2_profile

    tags = {
        name = "ec2-mlops"
    }

    root_block_device {
        volume_size = var.ec2_volume_size
    }

    user_data = file("modules/ec2/user_data.sh")
}
