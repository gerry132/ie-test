
variable "canary_name" {
  type    = string
  default = "site-health-canary"
}

variable "target_url" {
  type        = string
  description = "Full URL to check, e.g. https://content.uat.ireland.ie/"
}



# Optional — likely won’t deliver in your org account, but left here if you want to try.
variable "sms_phone_number" {
  type        = string
  description = "E.164 phone number (e.g. +353...)"
  default     = ""
}


resource "aws_sns_topic" "alerts" {
  name = "${var.canary_name}-alerts"
}


resource "aws_sns_topic_subscription" "sms" {
  count     = var.sms_phone_number != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "sms"
  endpoint  = var.sms_phone_number
}


resource "aws_s3_bucket" "canary_artifacts" {
  bucket = "canary-artifacts-${var.environment_name}"
}

resource "aws_s3_bucket_public_access_block" "canary_artifacts" {
  bucket                  = aws_s3_bucket.canary_artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_caller_identity" "current" {}

############################################
# IAM role for synthetics
############################################

resource "aws_iam_role" "canary_role" {
  name = "${var.canary_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = ["synthetics.amazonaws.com", "lambda.amazonaws.com"] }
      Action    = "sts:AssumeRole"
    }]
  })
}


resource "aws_iam_role_policy" "canary_put_metric_data" {
  role = aws_iam_role.canary_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "AllowPutMetricData"
      Effect   = "Allow"
      Action   = ["cloudwatch:PutMetricData"]
      Resource = "*"
    }]
  })
}


resource "aws_iam_role_policy_attachment" "synthetics_full" {
  role       = aws_iam_role.canary_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchSyntheticsFullAccess"
}

resource "aws_iam_role_policy" "canary_s3_policy" {
  role = aws_iam_role.canary_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetBucketLocation",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.canary_artifacts.arn,
          "${aws_s3_bucket.canary_artifacts.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_synthetics_canary" "site" {
  name                 = var.canary_name
  artifact_s3_location = "s3://${aws_s3_bucket.canary_artifacts.bucket}/"
  execution_role_arn   = aws_iam_role.canary_role.arn

  runtime_version = "syn-python-selenium-8.0"
  handler         = "index.handler"

  s3_bucket = var.canary_code_s3_bucket
  s3_key    = var.canary_code_s3_key

  schedule {
    expression = "rate(1 minute)"
  }

    run_config {
    timeout_in_seconds = 60
    environment_variables = {
        TARGET_URL     = var.target_url
        REDEPLOY_STAMP = timestamp()
    }
    }

  start_canary = true
}


resource "aws_cloudwatch_metric_alarm" "canary_failed" {
  alarm_name          = "irelandie-${var.environment_name}-heartbeat-failed"
  alarm_description   = "Canary failed for ${var.target_url}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  threshold           = 1
  treat_missing_data  = "breaching"

  namespace   = "CloudWatchSynthetics"
  metric_name = "Failed"
  statistic   = "Sum"
  period      = 60


  dimensions = {
    CanaryName = aws_synthetics_canary.site.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn] # remove if you only want DOWN alerts
}
