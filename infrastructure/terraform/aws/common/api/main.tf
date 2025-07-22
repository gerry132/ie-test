resource "aws_s3_bucket" "api-logs" {
  bucket  = "${var.environment_name}ireland-ie-api-logs"
}

resource "aws_s3_bucket_ownership_controls" "api-controls" {
  bucket = aws_s3_bucket.api-logs.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_policy" "alb_logs" {
  bucket = aws_s3_bucket.api-logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowELBLogging"
        Effect    = "Allow"
        Principal = {
          Service = "logdelivery.elasticloadbalancing.amazonaws.com"
        }
        Action = [
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.api-logs.arn}/*"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      },
      {
        Sid       = "AllowELBListBucket"
        Effect    = "Allow"
        Principal = {
          Service = "logdelivery.elasticloadbalancing.amazonaws.com"
        }
        Action = "s3:ListBucket"
        Resource = aws_s3_bucket.api-logs.arn
      }
    ]
  })
}

data "aws_caller_identity" "current" {}


resource "aws_ecs_task_definition" "api_task" {
  family                   = "${var.environment_name}-api"
  execution_role_arn       = var.execution_role
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions    = var.container_definitions
}

resource "aws_lb" "api" {
  name                = "${var.environment_name}-api"
  subnets             = var.subnets
  security_groups     = [var.lb_security_groups]
  internal            = false

  access_logs {
    bucket  = aws_s3_bucket.api-logs.bucket
    prefix  = "cms-lb"
    enabled = true
  }

  tags = {
    Name            = "${var.environment_name}-api-lb"
    Environment     = var.environment_name
  }
}



resource "aws_ecs_service" "api" {
  name                    = "${var.environment_name}-api"
  cluster                 = var.cluster.arn
  task_definition         = aws_ecs_task_definition.api_task.arn
  desired_count           = 1
  launch_type             = "FARGATE"
  force_new_deployment    = true


  load_balancer {
    target_group_arn    = aws_lb_target_group.api_target_group.arn
    container_name      = "${var.environment_name}-${var.project_name}"
    container_port      = 8000
  }

  network_configuration {
    security_groups     = [var.ecs_security_groups]
    subnets             = var.subnets
    assign_public_ip    = true
  }
}


resource "aws_lb_listener_certificate" "api_cert" {
  listener_arn    = aws_lb_listener.api_listener.arn
  certificate_arn = aws_acm_certificate.api.arn
}


resource "aws_lb_listener_rule" "api_forward" {
  listener_arn    = aws_lb_listener.api_listener.arn
  priority        = 2

  action {
    type                = "forward"
    target_group_arn    = aws_lb_target_group.api_target_group.arn
  }

  condition {
    host_header {
      values  = [var.api_domain]
    }
  }
}

resource "aws_lb_listener" "api_listener" {
  load_balancer_arn     = aws_lb.api.arn
  port                  = 443
  protocol              = "HTTPS"
  ssl_policy            = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn       = aws_acm_certificate.api.arn

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      status_code  = 503
    }
  }
}


  resource "aws_lb_target_group" "api_target_group" {
    name            = "api-target-group"
    port            = 8000
    protocol        = "HTTP"
    target_type     = "ip"
    vpc_id          = var.vpc_id

    health_check {
      interval                = 120
      path                    = "/health-check/"
      protocol                = "HTTP"
      timeout                 = 60
      healthy_threshold       = 2
      unhealthy_threshold     = 3
      matcher                 = "200-399"
    }
  }

resource "aws_acm_certificate" "api" {
  domain_name                 = var.api_domain

  validation_method           = "DNS"

  lifecycle {
    create_before_destroy   = true
  }
}
