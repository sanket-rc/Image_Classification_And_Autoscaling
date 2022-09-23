# Creates a key pair in aws, we use this public key's priv key to login to vm's
resource "aws_key_pair" "ssh-key" {
  key_name   = "ssh-key"
  public_key = var.ssh_public_key
}

resource "local_file" "config_file_web" {
  content = yamlencode({
    "REGION_NAME" : var.region,
    "REQUEST_QUEUE" : aws_sqs_queue.request_queue.url,
    "RESPONSE_QUEUE" : aws_sqs_queue.response_queue.url,
    "INPUT_BUCKET" : aws_s3_bucket.pro1_input.bucket,
    "OUTPUT_BUCKET" : aws_s3_bucket.pro1_output.bucket,
    "CLASSIFIER_AMI" : aws_ami_from_instance.apptier_ami.id,
    "TERMINATE_REQUEST_QUEUE" : aws_sqs_queue.terminate_request_queue.url,
    "TERMINATE_CONFIRM_QUEUE" : aws_sqs_queue.terminate_confirm_queue.url,
    "AWS_ACCESS_KEY_ID" : var.aws_access_key_id,
    "AWS_SECRET_ACCESS_KEY" : var.aws_secret_key_id
    "KEY_NAME" : aws_key_pair.ssh-key.key_name
    "VPC_ID" : aws_vpc.vpc.id
    "APP_SUBNET_ID" : aws_subnet.app_tier.id
    "WEB_SUBNET_ID" : aws_subnet.web_tier.id
  })
  filename = "config_web.yaml"
}

resource "local_file" "config_file_app" {
  content = yamlencode({
    "REGION_NAME" : var.region,
    "REQUEST_QUEUE" : aws_sqs_queue.request_queue.url,
    "RESPONSE_QUEUE" : aws_sqs_queue.response_queue.url,
    "INPUT_BUCKET" : aws_s3_bucket.pro1_input.bucket,
    "OUTPUT_BUCKET" : aws_s3_bucket.pro1_output.bucket,
    "TERMINATE_REQUEST_QUEUE" : aws_sqs_queue.terminate_request_queue.url,
    "TERMINATE_CONFIRM_QUEUE" : aws_sqs_queue.terminate_confirm_queue.url,
    "AWS_ACCESS_KEY_ID" : var.aws_access_key_id,
    "AWS_SECRET_ACCESS_KEY" : var.aws_secret_key_id
  })
  filename = "config_app.yaml"
}
