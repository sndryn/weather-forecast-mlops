variable "ec2_ami" {
    type    = string
    default = "ami-02c7683e4ca3ebf58"
}

variable "ec2_instance_type" {
    type    = string
    default = "t3a.large"
}

variable "ec2_subnet_id" {
    type    = string
}

variable "ec2_profile" {
    type    = string
}

variable "ec2_sg_id" {
    type    = string
}

variable "ssm_instance_key_name" {
    type    = string
}

variable "ec2_volume_size" {
    type    = number
    default = 12
}
