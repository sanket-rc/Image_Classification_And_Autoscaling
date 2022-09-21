output "web_server_ec2_details" {
  value = aws_instance.web_server_ec2.public_ip
}

output "request_queue" {
  value = aws_sqs_queue.request_queue.url
}

output "response_queue" {
  value = aws_sqs_queue.response_queue.url
}

output "scale_queue" {
  value = aws_sqs_queue.scale_queue.url
}

output "s3_url_input" {
  value = aws_s3_bucket.pro1_input.bucket
}

output "s3_url_output" {
  value = aws_s3_bucket.pro1_output.bucket
}

output "app_tier_ami" {
  value = aws_ami_from_instance.apptier_ami.arn
}