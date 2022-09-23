resource "aws_s3_bucket" "pro1_input" {
  bucket        = var.input_bucket_name
  force_destroy = true
  tags = {
    Name = var.input_bucket_name
  }
}

resource "aws_s3_bucket" "pro1_output" {
  bucket        = var.output_bucket_name
  force_destroy = true
  tags = {
    Name = var.output_bucket_name
  }
}