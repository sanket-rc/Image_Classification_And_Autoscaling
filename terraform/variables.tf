variable "webserver_instance_type" {
  type    = string
  default = "t2.micro"
}
variable "ssh_public_key" {
  type = string
}

variable "vpc_cidr_block" {
  type    = string
  default = "10.0.0.0/16"
}

variable "webtier_ami_id" {
  type = string
  default = "ami-05fa00d4c63e32376"
}