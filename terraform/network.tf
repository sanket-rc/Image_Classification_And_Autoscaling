# creates the required vpc
resource "aws_vpc" "vpc" {
  cidr_block = var.vpc_cidr_block
  tags = {
    Name = "p1_vpc"
  }
}

# creates a subnet in the vpc for web tier
resource "aws_subnet" "web_tier" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  tags = {
    Name = "p1_webtier"
  }
}

# creates a subnet in the vpc for web tier
resource "aws_subnet" "app_tier" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
  tags = {
    Name = "p1_apptier"
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
  ingress {
    description = "Flask connection"
    from_port   = 3000
    protocol    = "tcp"
    to_port     = 3000
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

#resource "aws_security_group_rule" "flask_ingress" {
#  from_port         = 5000
#  protocol          = "tcp"
#  security_group_id = aws_security_group.pro1_security_group.id
#  to_port           = 5000
#  type              = "ingress"
#}

resource "aws_internet_gateway" "internet-gateway" {
  vpc_id = aws_vpc.vpc.id
  tags = {
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
resource "aws_route_table_association" "public-webtier_subnet-route-table-association" {
  subnet_id      = aws_subnet.web_tier.id
  route_table_id = aws_route_table.public-route-table.id
}

resource "aws_route_table_association" "public-apptier_subnet-route-table-association" {
  subnet_id      = aws_subnet.app_tier.id
  route_table_id = aws_route_table.public-route-table.id
}
