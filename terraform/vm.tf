# Creates a key pair in aws, we use this public key's priv key to login to vm's
resource "aws_key_pair" "ssh-key" {
  key_name   = "ssh-key"
  public_key = var.ssh_public_key
}

# creates the required vpc
resource "aws_vpc" "vpc" {
  cidr_block = var.vpc_cidr_block
  tags       = {
    Name = "p1_vpc"
  }
}

# creates a subnet in the vpc for web tier
resource "aws_subnet" "web_tier" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  tags                    = {
    Name = "p1_webtier"
  }
}

# Creates the ec2 instance
resource "aws_instance" "web_server_ec2" {
  ami                         = var.webtier_ami_id
  instance_type               = var.webserver_instance_type
  key_name                    = "ssh-key"
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.pro1_security_group.id]
  subnet_id                   = aws_subnet.web_tier.id
  depends_on                  = [local_file.config_file_web, aws_security_group.pro1_security_group]

    provisioner "file" {
      source      = "config_web.yaml"
      destination = "/home/ec2-user/config.yaml"
      connection {
        type        = "ssh"
        user        = "ec2-user"
        host        = self.public_ip
        private_key = file("id_rsa.pem")
      }
    }

  tags = {
    Name = "Webserver"
  }
}

# creates the security group
resource "aws_security_group" "pro1_security_group" {
  name        = "pro1_sec_group"
  description = "Allow SSH inbound traffic"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    description = "SSH from the internet"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "pro1_sec_group"
  }
}

resource "aws_internet_gateway" "internet-gateway" {
  vpc_id = aws_vpc.vpc.id
  tags   = {
    Name = "internet_gateway"
  }
}

resource "aws_route_table" "public-route-table" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.internet-gateway.id
  }
  tags = {
    Name = "Public Route Table"
  }
}
resource "aws_route_table_association" "public-subnet-1-route-table-association" {
  subnet_id      = aws_subnet.web_tier.id
  route_table_id = aws_route_table.public-route-table.id
}
