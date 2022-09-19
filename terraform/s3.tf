resource "aws_s3_bucket" "pro1_input" {
  bucket = "pro1input"

  tags = {
    Name = "pro1input"
  }
}

resource "aws_s3_bucket" "pro1_output" {
  bucket = "pro1output"

  tags = {
    Name = "pro1output"
  }
}