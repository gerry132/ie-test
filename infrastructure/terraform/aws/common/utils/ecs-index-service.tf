resource "aws_ecs_task_definition" "publish_task" {
  family                   = "${var.environment_name}-publish"
  execution_role_arn       = var.execution_role
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"  # Task-level CPU
  memory                   = "512"  # Task-level memory

  container_definitions    = var.publish_task_definitions
}

resource "aws_ecs_task_definition" "index_task" {
  family                   = "${var.environment_name}-update-indexes"
  execution_role_arn       = var.execution_role
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"  # Task-level CPU
  memory                   = "512"  # Task-level memory

  container_definitions    = var.container_definitions
}

# hourly event trigger
resource "aws_cloudwatch_event_rule" "hourly_trigger" {
  name        = "${var.environment_name}-hourly-publish"
  description = "Triggers the ECS task to publish scheduled pages"
  schedule_expression = "rate(60 minutes)"
}

# event bridge weekly trigger

resource "aws_cloudwatch_event_rule" "weekly_trigger" {
  name        = "${var.environment_name}-weekly-update-indexes"
  description = "Triggers the ECS task to update indexes once per week"
  schedule_expression = "cron(0 3 ? * 1 *)" # Adjust cron expression as needed
}

resource "aws_cloudwatch_event_target" "ecs_task_target_publish" {
  rule      = aws_cloudwatch_event_rule.hourly_trigger.name
  target_id = "publish-task"
  arn       = var.cluster.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.publish_task.arn
    launch_type         = "FARGATE"

    network_configuration {
        security_groups     = [var.security_groups]
        subnets             = var.subnets
    }
  }
    role_arn = aws_iam_role.eventbridge_to_ecs.arn
}


resource "aws_cloudwatch_event_target" "ecs_task_target" {
  rule      = aws_cloudwatch_event_rule.weekly_trigger.name
  target_id = "index-update-task"
  arn       = var.cluster.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.index_task.arn
    launch_type         = "FARGATE"

    network_configuration {
        security_groups     = [var.security_groups]
        subnets             = var.subnets
    }
  }
    role_arn = aws_iam_role.eventbridge_to_ecs.arn
}

resource "aws_iam_role" "eventbridge_to_ecs" {
  name = "${var.environment_name}-eventbridge-to-ecs"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "events.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "eventbridge_to_ecs_policy" {
  role = aws_iam_role.eventbridge_to_ecs.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "ecs:RunTask",
          "iam:PassRole"
        ]
        Resource = [
          aws_ecs_task_definition.index_task.arn,
          aws_ecs_task_definition.publish_task.arn,
          var.execution_role
        ]
      }
    ]
  })
}


variable "environment_name" {}
variable "task_cpu" {}
variable "region" { default = "eu-west-1" }
variable "task_memory" {}
variable "subnets" {}
variable "security_groups" {}
variable "container_definitions" {}
variable "publish_task_definitions" {}
variable "cluster" {}
variable "execution_role" {}
