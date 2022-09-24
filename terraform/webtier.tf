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
    source      = "../python/web_tier"
    destination = "/home/ec2-user"
    connection {
      type        = "ssh"
      user        = "ec2-user"
      host        = self.public_ip
      private_key = file("id_rsa.pem")
    }
  }

  provisioner "file" {
    source      = "config_web.yaml"
    destination = "/home/ec2-user/web_tier/config.yaml"
    connection {
      type        = "ssh"
      user        = "ec2-user"
      host        = self.public_ip
      private_key = file("id_rsa.pem")
    }
  }
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "ec2-user"
      host        = self.public_ip
      private_key = file("id_rsa.pem")
    }
    inline = [
      "chmod +x /home/ec2-user/web_tier",
      "bash /home/ec2-user/web_tier/startup_webtier.sh",
    ]
  }

  tags = {
    Name = "Webserver"
  }
}