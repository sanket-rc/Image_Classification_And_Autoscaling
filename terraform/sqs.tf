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

resource "aws_sqs_queue" "scale_queue" {
  name                      = "scale_queue"
  delay_seconds             = 90
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10

  tags = {
    Project = "project1"
    name    = "scale_queue"
  }
}