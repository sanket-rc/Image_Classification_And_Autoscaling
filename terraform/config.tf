resource "local_file" "config_file" {
  content = yamlencode({
    "request_queue" : aws_sqs_queue.request_queue.url,
    "response_queue" : aws_sqs_queue.response_queue.url,
    "scale_queue" : aws_sqs_queue.scale_queue.url,
    "s3_url_input" : aws_s3_bucket.pro1_input.bucket_prefix,
    "s3_url_output" : aws_s3_bucket.pro1_output.bucket_prefix
  })
  filename = "foo.yaml"
}
