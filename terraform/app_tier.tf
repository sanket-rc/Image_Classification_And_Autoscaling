# Creates the ec2 instance
resource "aws_instance" "app_ec2" {
  ami                         = var.apptier_ami_id
  instance_type               = var.webserver_instance_type
  key_name                    = "ssh-key"
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.pro1_security_group.id]
  subnet_id                   = aws_subnet.app_tier.id
  depends_on                  = [local_file.config_file_app, aws_security_group.pro1_security_group]
  user_data = file("startup_apptier.sh")

  provisioner "file" {
    source      = "../python/app_tier"
    destination = "/home/ubuntu"
    connection {
      type        = "ssh"
      user        = "ubuntu"
      host        = self.public_ip
      private_key = file("id_rsa.pem")
    }
  }

  provisioner "file" {
    source      = "config_app.yaml"
    destination = "/home/ubuntu/app_tier/config.yaml"
    connection {
      type        = "ssh"
      user        = "ubuntu"
      host        = self.public_ip
      private_key = file("id_rsa.pem")
    }
  }

  tags = {
    Name = "apptier_ec2_1"
  }
}

resource "aws_ami_from_instance" "apptier_ami" {
  depends_on         = [aws_instance.app_ec2]
  name               = "p1_apptier_aakash"
  source_instance_id = aws_instance.app_ec2.id
}