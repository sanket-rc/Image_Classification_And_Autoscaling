resource "local_file" "config_file_web" {
  content = yamlencode({
    "request_queue" : aws_sqs_queue.request_queue.url,
    "response_queue" : aws_sqs_queue.response_queue.url,
    "scale_queue" : aws_sqs_queue.scale_queue.url,
    "s3_url_input" : aws_s3_bucket.pro1_input.bucket,
    "s3_url_output" : aws_s3_bucket.pro1_output.bucket,
    "app_tier _ami" : aws_ami_from_instance.apptier_ami.id
  })
  filename = "config_web.yaml"
}

resource "local_file" "config_file_app" {
  content = yamlencode({
    "request_queue" : aws_sqs_queue.request_queue.url,
    "response_queue" : aws_sqs_queue.response_queue.url,
    "scale_queue" : aws_sqs_queue.scale_queue.url,
    "s3_url_input" : aws_s3_bucket.pro1_input.bucket,
    "s3_url_output" : aws_s3_bucket.pro1_output.bucket,
  })
  filename = "config_app.yaml"
}
