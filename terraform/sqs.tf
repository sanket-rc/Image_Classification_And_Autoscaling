resource "aws_sqs_queue" "request_queue" {
  name                      = "request_queue"
  delay_seconds             = 90
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10

  tags = {
    Project = "project1"
    name    = "request_queue"
  }
}

resource "aws_sqs_queue" "response_queue" {
  name                      = "response_queue"
  delay_seconds             = 90
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10

  tags = {
    Project = "project1"
    name    = "response_queue"
  }
}

resource "aws_sqs_queue" "terminate_request_queue" {
  name                      = "terminate_request_queue"
  delay_seconds             = 90
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10

  tags = {
    Project = "project1"
    name    = "terminate_request_queue"
  }
}
resource "aws_sqs_queue" "terminate_confirm_queue" {
  name                      = "terminate_confirm_queue"
  delay_seconds             = 90
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10

  tags = {
    Project = "project1"
    name    = "terminate_confirm_queue"
  }
}