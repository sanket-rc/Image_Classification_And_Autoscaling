resource "aws_s3_bucket" "pro1_input" {
  bucket = "pro1inputtest"

  tags = {
    Name = "pro1input"
  }
}

resource "aws_s3_bucket" "pro1_output" {
  bucket = "pro1outputtest"

  tags = {
    Name = "pro1output"
  }
}