terraform {
  required_version = ">=1.1"
  required_providers {
    aws         = ">=4.0.0"
    random      = ">=3.1.0"
    template    = ">=2.2.0"
  }
}

provider "aws" {
  alias  = "virginia"
  region = "us-east-1"
}


terraform {
  backend "s3" {
    bucket                      = "ireland-ie-prod-infrastructure"
    key                         = "website/terraform.tfstate"
    region                      = "eu-west-1"
    encrypt                     = true
  }
}

data "aws_caller_identity" "current" {}

data "aws_elb_service_account" "elb" {}


locals {
  account_id                    = data.aws_caller_identity.current.account_id
  elb_account_arn               = data.aws_elb_service_account.elb.arn
  environment_name              = "prod"
  app_aws_username              = "PROD_APP_USER"
  project_domain                = "content.ireland.ie"
  domain_ireland_ie             = "ireland.ie"
  africa_day_domain             = "africaday.ie"
  project_name                  = "ireland-ie"

  region                        = "eu-west-1"
  # DB
  db_instance_class             = "db.m6g.large"
  # CACHE
  cache_instance_class          = "cache.r6g.large"
  # ECS
  ecr_repository_name           = "${local.environment_name}-${local.project_name}"
  autoscaling_max_capacity      = 12
  autoscaling_min_capacity      = 4
  autoscaling_target_value      = 60
  service_contrainer_port       = 8000
  task_cpu                      = 2048  # min 1024
  task_memory                   = 4096  # min 2048

  # APP
  health_check_path             = "/health-check/"
  SETTINGS_DEBUG                = 1
  SETTINGS_DEBUG_TOOLBAR        = 0
  SETTINGS_USE_S3               = 1
  SETTINGS_USE_CACHE            = 1
  gov_network_cird_blocks       = [
    "169.254.192.0/18",
    "137.191.224.0/19",
    "193.178.64.0/19",
    "193.178.96.0/20",
    "139.162.239.108/32",
  ]
  non_gov_network_cird_blocks   = {
    dfa_main = {
      description = "DFA main IP address"
      cidr_blocks = ["62.23.128.137/32"]
    },
    dfa_wifi = {
      description = "DFA WiFi IP address"
      cidr_blocks = ["80.169.58.154/32"]
    },
    reinaldo_dev = {
      description = "Reinaldo Sanches - OGCIO"
      cidr_blocks = ["172.105.95.186/32", "89.101.167.251/32"]
    },
    gerry_dev = {
      description = "Gerry Mcbride - OGCIO"
      cidr_blocks = ["52.49.120.79/32", "37.228.234.5/32", "93.107.211.192/32"]
    },
    deekshana_dev = {
      description = "Deekshana - Sidero"
      cidr_blocks  = ["80.233.53.212/32", "80.233.57.212/32"]
    }
  }
}

# -----------------------------------------------------------------------------
# Values to fill after running terraform is ran, used for codebuild and secrets
# -----------------------------------------------------------------------------

resource "aws_ssm_parameter" "CLOUDFRONT_ID" {
  name        = "${local.environment_name}_CLOUDFRONT_ID"
  description = "For use in Codebuild buildspec - ${local.environment_name}"
  type        = "SecureString"
  value       = "CHANGE-ME"

  lifecycle {
    ignore_changes = [
      value,
    ]
  }
}


resource "aws_ssm_parameter" "OPENSEARCH_ENDPOINT" {
  name        = "${local.environment_name}_OPENSEARCH_ENDPOINT"
  description = "For use in Codebuild buildspec - ${local.environment_name}"
  type        = "SecureString"
  value       = "CHANGE-ME"

  lifecycle {
    ignore_changes = [
      value,
    ]
  }
}

resource "aws_ssm_parameter" "OPENSEARCH_KEY" {
  name        = "${local.environment_name}_OPENSEARCH_KEY"
  description = "For use in Codebuild buildspec - ${local.environment_name}"
  type        = "SecureString"
  value       = "CHANGE-ME"

  lifecycle {
    ignore_changes = [
      value,
    ]
  }
}

resource "aws_ssm_parameter" "OPENSEARCH_SECRET" {
  name        = "${local.environment_name}_OPENSEARCH_SECRET"
  description = "For use in Codebuild buildspec - ${local.environment_name}"
  type        = "SecureString"
  value       = "CHANGE-ME"

  lifecycle {
    ignore_changes = [
      value,
    ]
  }
}


resource "aws_ssm_parameter" "DOCKER_IMAGE_URL" {
  name        = "${local.environment_name}_DOCKER_IMAGE_URL"
  description = "For use in Codebuild buildspec - ${local.environment_name}"
  type        = "SecureString"
  value       = "alpine:3.11"

  lifecycle {
    ignore_changes = [
      value,
    ]
  }
}

resource "aws_ssm_parameter" "DEFAULT_FROM_EMAIL" {
  name        = "${local.environment_name}_DEFAULT_FROM_EMAIL"
  description = "For use in Codebuild buildspec - ${local.environment_name}"
  type        = "SecureString"
  value       = "CHANGE-ME"

  lifecycle {
    ignore_changes = [
      value,
    ]
  }
}

resource "aws_ssm_parameter" "AWS_SECRET_ACCESS_KEY" {
  name        = "${local.environment_name}_AWS_SECRET_ACCESS_KEY"
  description = "For use in Codebuild buildspec - ${local.environment_name}"
  type        = "SecureString"
  value       = "CHANGE-ME"

  lifecycle {
    ignore_changes = [
      value,
    ]
  }
}

resource "aws_ssm_parameter" "AWS_ACCESS_KEY_ID" {
  name        = "${local.environment_name}_AWS_ACCESS_KEY_ID"
  description = "For use in Codebuild buildspec - ${local.environment_name}"
  type        = "SecureString"
  value       = "CHANGE-ME"

  lifecycle {
    ignore_changes = [
      value,
    ]
  }
}


# -----------------------------------------------------------------------------
# Systems Manager - Parameter Store
# -----------------------------------------------------------------------------

resource "aws_ssm_parameter" "AWS_DEFAULT_REGION" {
  name        = "${local.environment_name}_AWS_DEFAULT_REGION"
  description = "For use in Codebuild buildspec - ${local.environment_name}"
  type        = "SecureString"
  value       = local.region
}

resource "aws_ssm_parameter" "AWS_ACCOUNT_ID" {
  name        = "${local.environment_name}_AWS_ACCOUNT_ID"
  description = "For use in Codebuild buildspec - ${local.environment_name}"
  type        = "SecureString"
  value       = local.account_id
}

resource "aws_ssm_parameter" "IMAGE_REPO_NAME" {
  name        = "${local.environment_name}_IMAGE_REPO_NAME"
  description = "For use in Codebuild buildspec - ${local.environment_name}"
  type        = "SecureString"
  value       = local.ecr_repository_name
}


# -----------------------------------------------------------------------------
# Networks
# -----------------------------------------------------------------------------

module "network" {
  source            = "github.com/ogcio/terraform-aws-public-network"
  environment_name  = local.environment_name
}


# -----------------------------------------------------------------------------
# Security groups
# -----------------------------------------------------------------------------

resource "aws_security_group" "lb" {
    name    = "${local.environment_name}-lb"
    vpc_id  = module.network.vpc_id
}

resource "aws_security_group" "lb_gov_network" {
    name    = "${local.environment_name}-lb-gov-network"
    vpc_id  = module.network.vpc_id
}

resource "aws_security_group" "ecs" {
    name    = "${local.environment_name}-ecs"
    vpc_id  = module.network.vpc_id
}

resource "aws_security_group" "db" {
    name    = "${local.environment_name}-db"
    vpc_id  = module.network.vpc_id
}

resource "aws_security_group" "redis" {
    name    = "${local.environment_name}-redis"
    vpc_id  = module.network.vpc_id
}


# -----------------------------------------------------------------------------
# Security group rules
# -----------------------------------------------------------------------------

# Public access rules

resource "aws_security_group_rule" "internet_to_lb_80" {
  type                      = "ingress"
  from_port                 = 80
  to_port                   = 80
  protocol                  = "tcp"
  security_group_id         = aws_security_group.lb.id
  cidr_blocks               = ["0.0.0.0/0"]
}


resource "aws_security_group_rule" "internet_to_lb_443" {
  type                      = "ingress"
  from_port                 = 443
  to_port                   = 443
  protocol                  = "tcp"
  security_group_id         = aws_security_group.lb.id
  cidr_blocks               = ["0.0.0.0/0"]
}

# Allow List IPs for restrict areas Gov Network

resource "aws_security_group_rule" "gov_network_to_lb_443" {
  description               = "Gov network"
  type                      = "ingress"
  from_port                 = 0
  to_port                   = 0
  protocol                  = "all"
  security_group_id         = aws_security_group.lb_gov_network.id
  cidr_blocks               = local.gov_network_cird_blocks
}

resource "aws_security_group_rule" "public_network_to_lb_443" {
  description               = "Network public network ip"
  type                      = "ingress"
  from_port                 = 0
  to_port                   = 0
  protocol                  = "all"
  security_group_id         = aws_security_group.lb_gov_network.id
  cidr_blocks               = ["${module.network.public_ip}/32"]
}

# Allow List IPs for restrict areas Outside Gov Network

resource "aws_security_group_rule" "non_gov_network_to_lb_443" {
  for_each = local.non_gov_network_cird_blocks

  description               = each.value.description
  type                      = "ingress"
  from_port                 = 0
  to_port                   = 0
  protocol                  = "all"
  security_group_id         = aws_security_group.lb_gov_network.id
  cidr_blocks               = each.value.cidr_blocks
}

# Internal thing rules

resource "aws_security_group_rule" "lb_to_internet" {
  type                      = "egress"
  from_port                 = 0
  to_port                   = 0
  protocol                  = "-1"
  cidr_blocks               = ["0.0.0.0/0"]
  security_group_id         = aws_security_group.lb.id
}

resource "aws_security_group_rule" "gov_network_lb_to_internet" {
  type                      = "egress"
  from_port                 = 0
  to_port                   = 0
  protocol                  = "-1"
  cidr_blocks               = ["0.0.0.0/0"]
  security_group_id         = aws_security_group.lb_gov_network.id
}

resource "aws_security_group_rule" "lb_to_ecs_8000" {
  type                      = "ingress"
  from_port                 = 8000
  to_port                   = 8000
  protocol                  = "tcp"
  source_security_group_id  = aws_security_group.lb.id
  security_group_id         = aws_security_group.ecs.id
}

resource "aws_security_group_rule" "gov_network_lb_to_ecs_8000" {
  type                      = "ingress"
  from_port                 = 8000
  to_port                   = 8000
  protocol                  = "tcp"
  source_security_group_id  = aws_security_group.lb_gov_network.id
  security_group_id         = aws_security_group.ecs.id
}

resource "aws_security_group_rule" "ecs_to_internet" {
  type                      = "egress"
  from_port                 = 0
  to_port                   = 0
  protocol                  = "-1"
  cidr_blocks               = ["0.0.0.0/0"]
  security_group_id         = aws_security_group.ecs.id
}

resource "aws_security_group_rule" "ecs_to_db_5432" {
  type                      = "ingress"
  from_port                 = 5432
  to_port                   = 5432
  protocol                  = "tcp"
  source_security_group_id  = aws_security_group.ecs.id
  security_group_id         = aws_security_group.db.id
}

resource "aws_security_group_rule" "ecs_to_redis_5432" {
  type                      = "ingress"
  from_port                 = 6379
  to_port                   = 6379
  protocol                  = "tcp"
  source_security_group_id  = aws_security_group.ecs.id
  security_group_id         = aws_security_group.redis.id
}


# -----------------------------------------------------------------------------
# Buckets
# -----------------------------------------------------------------------------

resource "aws_s3_bucket" "assets" {
  bucket  = "${local.environment_name}-${local.project_name}-assets"
}

resource "aws_s3_bucket_acl" "assets" {
  bucket = aws_s3_bucket.assets.id
  acl    = "public-read"
}

resource "aws_s3_bucket_cors_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket" "logs" {
  bucket  = "${local.environment_name}-${local.project_name}-ecs-logs"
}

resource "aws_s3_bucket_acl" "logs" {
  bucket = aws_s3_bucket.logs.id
  acl    = "private"
}

resource "aws_s3_bucket" "lb_logs" {
  bucket  = "${local.environment_name}-${local.project_name}-lb-logs"
}

resource "aws_s3_bucket_acl" "lb_logs" {
  bucket = aws_s3_bucket.lb_logs.id
  acl    = "private"
}

resource "aws_s3_bucket" "private_lb_logs" {
  bucket  = "${local.environment_name}-${local.project_name}-private-lb-logs"
}

resource "aws_s3_bucket" "cf-logs" {
  bucket  = "${local.environment_name}-${local.project_name}-cf-logs"
}

resource "aws_s3_bucket_acl" "cf-logs" {
  bucket = aws_s3_bucket.cf-logs.id
  acl    = "private"
  depends_on = [aws_s3_bucket_ownership_controls.cf_s3_bucket_acl_ownership]
}

# Resource to avoid error "AccessControlListNotSupported: The bucket does not allow ACLs"
resource "aws_s3_bucket_ownership_controls" "cf_s3_bucket_acl_ownership" {
  bucket = aws_s3_bucket.cf-logs.id
  rule {
    object_ownership = "ObjectWriter"
  }
}


resource "aws_s3_bucket_acl" "private_lb_logs" {
  bucket = aws_s3_bucket.private_lb_logs.id
  acl    = "private"
}


# Policies

resource "aws_s3_bucket_policy" "ecs_log_policy" {
  bucket = aws_s3_bucket.logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect      = "Allow",
        Principal   = {
          AWS       = local.elb_account_arn
        },
        Action      = "s3:*"
        Resource    = "${aws_s3_bucket.logs.arn}/*"
      },
      {
        Effect      = "Allow",
        Principal   = {
          AWS       = "arn:aws:iam::${local.account_id}:root"
        },
        Action      = "s3:*"
        Resource    = "${aws_s3_bucket.logs.arn}/*"
      },
    ]
  })
}

resource "aws_s3_bucket_policy" "lb_logs" {
  bucket = aws_s3_bucket.lb_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect      = "Allow",
        Principal   = {
          AWS       = local.elb_account_arn
        },
        Action      = "s3:*"
        Resource    = "${aws_s3_bucket.lb_logs.arn}/*/AWSLogs/${local.account_id}/*"
      },
      {
        Effect      = "Allow",
        Principal   = {
          AWS       = "arn:aws:iam::${local.account_id}:root"
        },
        Action      = "s3:*"
        Resource    = "${aws_s3_bucket.lb_logs.arn}/*/AWSLogs/${local.account_id}/*"
      },
    ]
  })
}

resource "aws_s3_bucket_policy" "private_lb_logs" {
  bucket = aws_s3_bucket.private_lb_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect      = "Allow",
        Principal   = {
          AWS       = local.elb_account_arn
        },
        Action      = "s3:*"
        Resource    = "${aws_s3_bucket.private_lb_logs.arn}/*/AWSLogs/${local.account_id}/*"
      },
      {
        Effect      = "Allow",
        Principal   = {
          AWS       = "arn:aws:iam::${local.account_id}:root"
        },
        Action      = "s3:*"
        Resource    = "${aws_s3_bucket.private_lb_logs.arn}/*/AWSLogs/${local.account_id}/*"
      },
    ]
  })
}


# -----------------------------------------------------------------------------
# Loadbalancers
# -----------------------------------------------------------------------------

resource "aws_subnet" "front_lb" {
  vpc_id     = module.network.vpc_id
  cidr_block = "10.0.16.0/24"
  tags = {
    Name = "NLB"
  }
}

resource "aws_route_table" "nlb_route_table" {
  vpc_id = module.network.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = module.network.internet_gateway
  }

  tags = {
    Name = "nlb-internet-route"
  }
}

resource "aws_route_table_association" "nlb" {
  subnet_id      = aws_subnet.front_lb.id
  route_table_id = aws_route_table.nlb_route_table.id
}


resource "aws_eip" "nlb" {
  vpc = true

  tags = {
    Name = "front_lb"
  }
}

resource "aws_lb" "net_lb" {
  name               = "net-lb"
  internal           = false
  load_balancer_type = "network"
  enable_deletion_protection = false

  subnet_mapping {
    subnet_id        = aws_subnet.front_lb.id
    allocation_id    = aws_eip.nlb.id
  }

  tags = {
    Environment = "uat"
  }
}

resource "aws_lb" "default" {
  name                = "${local.environment_name}-${local.project_name}"
  subnets             = module.network.public_subnet_ids
  security_groups     = [aws_security_group.lb_gov_network.id]
  internal            = false

  access_logs {
    bucket  = aws_s3_bucket.lb_logs.bucket
    prefix  = "cms-lb"
    enabled = true
  }

  tags = {
    Name            = "${local.environment_name}-${local.project_name}-lb"
    Environment     = local.environment_name
  }
}

resource "aws_lb" "public_sites" {
  name                = "${local.environment_name}-${local.project_name}-public-sites"
  subnets             = module.network.public_subnet_ids
  security_groups     = [aws_security_group.lb.id]
  internal            = false

  access_logs {
    bucket  = aws_s3_bucket.lb_logs.bucket
    prefix  = "public-sites-lb"
    enabled = true
  }

  tags = {
    Name            = "${local.environment_name}-${local.project_name}-lb-public-sites"
    Environment     = local.environment_name
  }
}


# -----------------------------------------------------------------------------
# Target groups
# -----------------------------------------------------------------------------

# All sites points to this
resource "aws_lb_target_group" "front_lb_http" {
  name            = "${local.environment_name}-${local.project_name}-nlb-http"
  port            = 80
  protocol        = "TCP"
  target_type     = "alb"
  vpc_id          = module.network.vpc_id
}

resource "aws_lb_target_group_attachment" "flb_http" {
  target_group_arn = aws_lb_target_group.front_lb_http.arn
  target_id        = aws_lb.public_sites.arn
  port             = 80
}

resource "aws_lb_target_group" "front_lb" {
  name            = "${local.environment_name}-${local.project_name}-nlb"
  port            = 443
  protocol        = "TCP"
  target_type     = "alb"
  vpc_id          = module.network.vpc_id
}

resource "aws_lb_target_group_attachment" "flb" {
  target_group_arn = aws_lb_target_group.front_lb.arn
  target_id        = aws_lb.public_sites.arn
  port             = 443
}


resource "aws_lb_target_group" "default" {
  name            = "${local.environment_name}-${local.project_name}"
  port            = 80
  protocol        = "HTTP"
  target_type     = "ip"
  vpc_id          = module.network.vpc_id

  health_check {
    interval                = 120
    path                    = local.health_check_path
    protocol                = "HTTP"
    timeout                 = 60
    healthy_threshold       = 2
    unhealthy_threshold     = 3
    matcher                 = "200-399"
  }

  lifecycle {
    create_before_destroy   = true
  }

  depends_on  = [
    aws_lb.default,
    aws_lb.public_sites
  ]
}

# Admin site should point here

resource "aws_lb_target_group" "default_admin" {
  name            = "${local.environment_name}-${local.project_name}-admin"
  port            = 80
  protocol        = "HTTP"
  target_type     = "ip"
  vpc_id          = module.network.vpc_id

  health_check {
    interval                = 120
    path                    = local.health_check_path
    protocol                = "HTTP"
    timeout                 = 60
    healthy_threshold       = 2
    unhealthy_threshold     = 3
    matcher                 = "200-399"
  }

  lifecycle {
    create_before_destroy   = true
  }

  depends_on  = [
    aws_lb.default,
    aws_lb.public_sites,
  ]
}


# -----------------------------------------------------------------------------
# SSL Certificates
# -----------------------------------------------------------------------------


resource "aws_acm_certificate" "project" {
  domain_name                 = local.project_domain
  validation_method           = "DNS"

  lifecycle {
    create_before_destroy   = true
  }
}


resource "aws_acm_certificate" "ireland_ie_ssl" {
  domain_name                 = "ireland.ie"
  subject_alternative_names = [
     "www.ireland.ie"
  ]
  validation_method           = "DNS"

  lifecycle {
    create_before_destroy   = true
  }
}

resource "aws_acm_certificate" "africa_day" {
    domain_name               = local.africa_day_domain
    subject_alternative_names = [
        "www.${local.africa_day_domain}"
    ]
    validation_method         = "DNS"

    lifecycle {
        create_before_destroy = true
    }
}

# -----------------------------------------------------------------------------
# Loadbalancer listeners and rules
# -----------------------------------------------------------------------------

resource "aws_lb_listener" "project_80" {
  load_balancer_arn   = aws_lb.default.arn
  port                = 80
  protocol            = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "project_net_http" {
  load_balancer_arn   = aws_lb.net_lb.arn
  port                = 80
  protocol            = "TCP"


  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.front_lb_http.arn
  }
}


resource "aws_lb_listener" "project_net" {
  load_balancer_arn   = aws_lb.net_lb.arn
  port                = 443
  protocol            = "TCP"


  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.front_lb.arn
  }
}


resource "aws_lb_listener" "project_443" {
  load_balancer_arn     = aws_lb.default.arn
  port                  = 443
  protocol              = "HTTPS"
  certificate_arn       = aws_acm_certificate.project.arn

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      status_code  = 503
    }
  }
}

# Public site listeners

resource "aws_lb_listener" "public_sites_80" {
  load_balancer_arn   = aws_lb.public_sites.arn
  port                = 80
  protocol            = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "public_sites_443" {
  load_balancer_arn     = aws_lb.public_sites.arn
  port                  = 443
  protocol              = "HTTPS"
  certificate_arn       = aws_acm_certificate.ireland_ie_ssl.arn

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      status_code  = 503
    }
  }
}

resource "aws_lb_listener_rule" "project_443" {
  listener_arn    = aws_lb_listener.project_443.arn
  priority        = 1

  action {
    type                = "forward"
    target_group_arn    = aws_lb_target_group.default_admin.arn
  }

  condition {
    host_header {
      values  = [local.project_domain]
    }
  }
}

# Force non-www to be used for admin site

resource "aws_lb_listener_rule" "www_project_443" {
  listener_arn    = aws_lb_listener.project_443.arn
  priority        = 2

  action {
    type              = "redirect"
    redirect {
      host            = local.project_domain
      status_code     = "HTTP_301"
    }
  }

  condition {
    host_header {
      values  = ["www.${local.project_domain}"]
    }
  }
}

# Public sites /admin redirects to admin site

resource "aws_lb_listener_rule" "www_ireland_ie_443_admin_redirect" {
  listener_arn    = aws_lb_listener.public_sites_443.arn
  priority        = 3

  action {
    type              = "redirect"
    redirect {
      host            = local.project_domain
      path            = "/admin/"
      status_code     = "HTTP_302"
    }
  }

  condition {
    path_pattern {
      values  = [
        "/admin/*",
      ]
    }
  }
}

# Public facing site rule

resource "aws_lb_listener_rule" "ireland_ie_www_redirect" {
  listener_arn    = aws_lb_listener.public_sites_443.arn
  priority        = 5

  action {
    type              = "redirect"
    redirect {
      host            = "www.${local.domain_ireland_ie}"
      status_code     = "HTTP_302"
    }
  }

  condition {
    host_header {
      values  = [local.domain_ireland_ie]
    }
  }
}

resource "aws_lb_listener_rule" "ireland_ie_443" {
  listener_arn    = aws_lb_listener.public_sites_443.arn
  priority        = 6

  action {
    type                = "forward"
    target_group_arn    = aws_lb_target_group.default.arn
  }

  condition {
    host_header {
      values  = ["www.${local.domain_ireland_ie}", local.domain_ireland_ie]
    }
  }
}

resource "aws_lb_listener_rule" "africa_day" {
    listener_arn = aws_lb_listener.public_sites_443.arn
    priority = 9

    action {
        type = "redirect"
        redirect {
            host = "www.${local.domain_ireland_ie}"
            path = "/africa-day"
            status_code = "HTTP_301"
        }
    }
    condition {
        host_header {
            values = [local.africa_day_domain, "www.${local.africa_day_domain}"]
        }
    }
}
# -----------------------------------------------------------------------------
# Listener certificates
# -----------------------------------------------------------------------------

resource "aws_lb_listener_certificate" "ireland_ie_certificate" {
  listener_arn    = aws_lb_listener.public_sites_443.arn
  certificate_arn = aws_acm_certificate.ireland_ie_ssl.arn
}

resource "aws_lb_listener_certificate" "admin_ireland_ie_certificate" {
  listener_arn    = aws_lb_listener.project_443.arn
  certificate_arn = aws_acm_certificate.project.arn
}

resource "aws_lb_listener_certificate" "africa_day_certificate" {
    listener_arn    = aws_lb_listener.public_sites_443.arn
    certificate_arn = aws_acm_certificate.africa_day.arn
}

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

# Random db password

resource "random_password" "password" {
  length  = 32
  special = true
}

resource "aws_ssm_parameter" "opensearch_master_user" {
  name        = "MASTER_USER"
  description = "opensearch_password"
  type        = "SecureString"
  value       = "${local.environment_name}-opensearch-user,${random_password.password.result}"
}

resource "aws_opensearch_domain" "opensearch" {
  domain_name = local.environment_name
  engine_version = "OpenSearch_2.7"

  cluster_config {
      instance_count = 3
      instance_type = "t3.medium.search"
      zone_awareness_enabled = true
      zone_awareness_config {
        availability_zone_count = 3
      }
  }
  ebs_options {
      ebs_enabled = true
      volume_size = 10
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
  advanced_security_options {
      enabled                        = true
      internal_user_database_enabled = true
      master_user_options {
          master_user_name     = "${local.environment_name}-opensearch-user"
          master_user_password = random_password.password.result
      }
    }
    access_policies = jsonencode(
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "AWS": "*"
          },
          "Action": "es:*",
          "Resource": "*"
        }
      ]
    })
}


resource "random_string" "random_db_password" {
  length           = 30
  special          = false
  override_special = "/@£$"
}

resource "aws_ssm_parameter" "random_db_password" {
  name        = "${local.environment_name}-${local.project_name}-db-password"
  description = "-"
  type        = "SecureString"
  value       = random_string.random_db_password.result

  tags = {
    environment = local.environment_name
  }
}

data "aws_ssm_parameter" "random_db_password" {
  name = aws_ssm_parameter.random_db_password.name

  depends_on = [
    aws_ssm_parameter.random_db_password
  ]
}

# Database

module "database" {
  source                = "github.com/ogcio/terraform-aws-db-instance-postgres-12-4"
  db_name               = "${local.environment_name}_ireland_ie"
  db_username           = "${local.environment_name}_ireland_ie_username"
  db_password           = data.aws_ssm_parameter.random_db_password.value
  db_instance_class     = local.db_instance_class
  db_engine_version     = "12.14"
  create_snapshot       = false
  name                  = "${local.environment_name}-db"
  subnets               = module.network.public_subnet_ids
  security_group_ids    = [aws_security_group.db.id]
}


locals {
    db_master_url   = "postgres://${module.database.db_username}:${data.aws_ssm_parameter.random_db_password.value}@${module.database.address}:${module.database.db_port}/${module.database.db_name}"
}


# -----------------------------------------------------------------------------
# Cache
# -----------------------------------------------------------------------------

resource "aws_elasticache_subnet_group" "redis" {
  name       = "redis-${local.environment_name}-subnet-group"
  subnet_ids = module.network.public_subnet_ids
}

resource "aws_elasticache_parameter_group" "redis" {
  name   = "redis-${local.environment_name}-parameter-group"
  family = "redis5.0"
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id                = "redis-${local.environment_name}"
  engine                    = "redis"
  node_type                 = local.cache_instance_class
  num_cache_nodes           = 1
  parameter_group_name      = aws_elasticache_parameter_group.redis.name
  engine_version            = "5.0.6"
  security_group_ids        = [aws_security_group.redis.id]
  apply_immediately         = true
  snapshot_window           = "02:00-04:00"
  snapshot_retention_limit  = 7
  subnet_group_name         = aws_elasticache_subnet_group.redis.name
}

locals {
  cache_address   = "${aws_elasticache_cluster.redis.cache_nodes.0.address}:6379"
}


# -----------------------------------------------------------------------------
# Logs
# -----------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "ecs" {
  name                = "/ecs/${local.environment_name}-${local.project_name}"
  retention_in_days   = 30
  tags = {
    Name    = "${local.environment_name}-${local.project_name}"
  }
}

resource "aws_cloudwatch_log_stream" "ecs" {
  name            = "${local.environment_name}-${local.project_name}"
  log_group_name  = aws_cloudwatch_log_group.ecs.name
}


# -----------------------------------------------------------------------------
# App user
# -----------------------------------------------------------------------------

resource "aws_iam_user" "opensearch" {
  name = "opensearch_${local.app_aws_username}"
}

resource "aws_iam_access_key" "opensearch" {
  user = aws_iam_user.opensearch.name
}

resource "aws_iam_user_policy" "opensearch_aws_user" {
  name = "opensearch-${local.project_name}-policy"
  user = "opensearch_${local.app_aws_username}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect":"Allow",
       "Action":[
          "es:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}


resource "aws_iam_user" "default" {
  name = local.app_aws_username
}

resource "aws_iam_access_key" "default" {
  user = aws_iam_user.default.name
}

resource "aws_iam_user_policy" "app_aws_user" {
  name = "${local.app_aws_username}-${local.project_name}-policy"
  user = local.app_aws_username
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect":"Allow",
       "Action":[
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:GetObjectAcl",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::${aws_s3_bucket.assets.bucket}/*"
    }
  ]
}
EOF
}


# -----------------------------------------------------------------------------
# ECR
# -----------------------------------------------------------------------------

resource "aws_ecr_repository" "project_app" {
  name                 = local.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}


# -----------------------------------------------------------------------------
# ECS
# -----------------------------------------------------------------------------

# Cluster

resource "aws_ecs_cluster" "default" {
  name                  = "${local.environment_name}-${local.project_name}"

  configuration {
    execute_command_configuration {
      logging    = "OVERRIDE"
      log_configuration {
        s3_bucket_name    = aws_s3_bucket.logs.bucket
        s3_key_prefix     = "cluster"
      }
    }
  }
}

# ECS Excecution role

data "aws_iam_policy_document" "task_execution" {
  version = "2012-10-17"

  statement {
    sid         = ""
    effect      = "Allow"
    actions     = ["sts:AssumeRole"]
    principals {
      type            = "Service"
      identifiers     = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "task_execution" {
  name                = "${local.environment_name}-${local.project_name}-task-execution"
  assume_role_policy  = data.aws_iam_policy_document.task_execution.json
}

resource "aws_iam_role_policy_attachment" "task_execution" {
  role        = aws_iam_role.task_execution.name
  policy_arn  = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource aws_iam_policy task_execution_access {
  policy  = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
        {
            "Effect":"Allow",
            "Action":[
                "ssm:GetParameters"
            ],
            "Resource": "arn:aws:ssm:${local.region}:${local.account_id}:*"
        }
    ]
}
POLICY
}


resource "aws_iam_role_policy_attachment" "default" {
  role        = aws_iam_role.task_execution.name
  policy_arn  = aws_iam_policy.task_execution_access.arn
}

# Random secret key

resource "random_string" "random_secret_key" {
  length           = 30
  special          = false
  override_special = "/@£$"
}


resource "aws_ssm_parameter" "random_secret_key" {
  name        = "${local.environment_name}-${local.project_name}-secret-key"
  description = "-"
  type        = "SecureString"
  value       = random_string.random_secret_key.result

  tags = {
    environment = local.environment_name
  }
}


data "aws_ssm_parameter" "random_secret_key" {
  name = aws_ssm_parameter.random_secret_key.name

  depends_on = [
    aws_ssm_parameter.random_secret_key
  ]
}


# -----------------------------------------------------------------------------
# Simple Email Service (SES)
# -----------------------------------------------------------------------------

resource "aws_iam_user" "smtp_user" {
  name = "${local.environment_name}-${local.project_name}-smtp-user"
}

resource "aws_iam_access_key" "smtp_user" {
  user = aws_iam_user.smtp_user.name
}

data "aws_iam_policy_document" "ses_sender" {
  statement {
    actions   = ["ses:SendRawEmail"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "ses_sender" {
  name        = "ses_sender"
  description = "Allows sending of e-mails via Simple Email Service"
  policy      = data.aws_iam_policy_document.ses_sender.json
}

resource "aws_iam_user_policy_attachment" "smtp_user_attach" {
  user       = aws_iam_user.smtp_user.name
  policy_arn = aws_iam_policy.ses_sender.arn
}


# Task definition

locals {
  SETTINGS_ALLOWED_HOSTS            = "*"
  SETTINGS_AWS_ACCESS_KEY_ID        = aws_ssm_parameter.AWS_ACCESS_KEY_ID.value
  SETTINGS_AWS_SECRET_ACCESS_KEY    = aws_ssm_parameter.AWS_SECRET_ACCESS_KEY.value
  SETTINGS_OPENSEARCH_SECRET        = aws_ssm_parameter.OPENSEARCH_SECRET.value
  SETTINGS_OPENSEARCH_ENDPOINT      = aws_ssm_parameter.OPENSEARCH_ENDPOINT.value
  SETTINGS_OPENSEARCH_KEY           = aws_ssm_parameter.OPENSEARCH_KEY.value
  SETTINGS_CLOUDFRONT_ID            = aws_ssm_parameter.CLOUDFRONT_ID.value
  SETTINGS_AWS_STATIC_BUCKET_NAME   = aws_s3_bucket.assets.id
  SETTINGS_BASE_URL                 = "https://${local.project_domain}"
  SETTINGS_CACHE_ADDRESS            = local.cache_address
  SETTINGS_DATABASE_URL             = local.db_master_url
  SETTINGS_SECRET_KEY               = data.aws_ssm_parameter.random_secret_key.value
  SETTINGS_CORS_ALLOWED_ORIGINS     = "${local.SETTINGS_BASE_URL},https://www.${local.project_domain}"
  SETTINGS_CORS_ALLOW_ALL_ORIGINS   = 0
  SETTINGS_EMAIL_HOST               = "email.${local.region}.amazonaws.com"
  SETTINGS_DEFAULT_FROM_EMAIL       = aws_ssm_parameter.DEFAULT_FROM_EMAIL.value
}

data "template_file" "task_definition" {
  template    = file("../common/templates/task_definition.tpl")

  vars = {
    ecr_image_url                       = "${local.account_id}.dkr.ecr.eu-west-1.amazonaws.com/${aws_ecr_repository.project_app.name}"
    log_group                           = aws_cloudwatch_log_group.ecs.name
    name                                = "${local.environment_name}-${local.project_name}"
    port                                = local.service_contrainer_port
    region                              = local.region
    task_cpu                            = local.task_cpu
    task_memory                         = local.task_memory
    assets_url                          = "assets.${local.domain_ireland_ie}"
    assets_s3_bucket                    = aws_s3_bucket.assets.id
    SETTINGS_ALLOWED_HOSTS              = local.SETTINGS_ALLOWED_HOSTS
    SETTINGS_AWS_ACCESS_KEY_ID          = local.SETTINGS_AWS_ACCESS_KEY_ID
    SETTINGS_AWS_SECRET_ACCESS_KEY      = local.SETTINGS_AWS_SECRET_ACCESS_KEY
    SETTINGS_AWS_STATIC_BUCKET_NAME     = local.SETTINGS_AWS_STATIC_BUCKET_NAME
    SETTINGS_OPENSEARCH_KEY             = local.SETTINGS_OPENSEARCH_KEY
    SETTINGS_OPENSEARCH_SECRET          = local.SETTINGS_OPENSEARCH_SECRET
    SETTINGS_OPENSEARCH_ENDPOINT        = local.SETTINGS_OPENSEARCH_ENDPOINT
    SETTINGS_CLOUDFRONT_ID              = local.SETTINGS_CLOUDFRONT_ID
    SETTINGS_BASE_URL                   = local.SETTINGS_BASE_URL
    SETTINGS_CACHE_ADDRESS              = local.SETTINGS_CACHE_ADDRESS
    SETTINGS_DATABASE_URL               = local.SETTINGS_DATABASE_URL
    SETTINGS_DEBUG                      = local.SETTINGS_DEBUG
    SETTINGS_DEBUG_TOOLBAR              = local.SETTINGS_DEBUG_TOOLBAR
    SETTINGS_SECRET_KEY                 = local.SETTINGS_SECRET_KEY
    SETTINGS_USE_CACHE                  = local.SETTINGS_USE_CACHE
    SETTINGS_USE_S3                     = local.SETTINGS_USE_S3
    SETTINGS_CORS_ALLOWED_ORIGINS       = local.SETTINGS_CORS_ALLOWED_ORIGINS
    SETTINGS_CORS_ALLOW_ALL_ORIGINS     = local.SETTINGS_CORS_ALLOW_ALL_ORIGINS
    SETTINGS_EMAIL_HOST                 = local.SETTINGS_EMAIL_HOST
    SETTINGS_DEFAULT_FROM_EMAIL         = local.SETTINGS_DEFAULT_FROM_EMAIL
  }
}

# Task definition

resource "aws_ecs_task_definition" "default" {
  family                   = "${local.environment_name}-${local.project_name}"
  execution_role_arn       = aws_iam_role.task_execution.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = local.task_cpu
  memory                   = local.task_memory
  container_definitions    = data.template_file.task_definition.rendered
}

# Service

resource "aws_ecs_service" "default" {
  name                    = "${local.environment_name}-${local.project_name}"
  cluster                 = aws_ecs_cluster.default.id
  task_definition         = aws_ecs_task_definition.default.arn
  desired_count           = local.autoscaling_min_capacity
  launch_type             = "FARGATE"
  force_new_deployment    = true

  load_balancer {
    target_group_arn    = aws_lb_target_group.default.arn
    container_name      = "${local.environment_name}-${local.project_name}"
    container_port      = local.service_contrainer_port
  }

  load_balancer {
    target_group_arn    = aws_lb_target_group.default_admin.arn
    container_name      = "${local.environment_name}-${local.project_name}"
    container_port      = local.service_contrainer_port
  }

  network_configuration {
    security_groups     = [aws_security_group.ecs.id]
    subnets             = module.network.private_subnet_ids
    assign_public_ip    = true
  }
}

# Service scaling

resource "aws_appautoscaling_target" "default" {
  max_capacity        = local.autoscaling_max_capacity
  min_capacity        = aws_ecs_service.default.desired_count
  resource_id         = "service/${aws_ecs_cluster.default.name}/${aws_ecs_service.default.name}"
  scalable_dimension  = "ecs:service:DesiredCount"
  service_namespace   = "ecs"
}


resource "aws_appautoscaling_policy" "cpu" {
  name                  = "${aws_ecs_service.default.name}-cpu-scaling-policy"
  policy_type           = "TargetTrackingScaling"
  resource_id           = aws_appautoscaling_target.default.resource_id
  scalable_dimension    = aws_appautoscaling_target.default.scalable_dimension
  service_namespace     = aws_appautoscaling_target.default.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value        = local.autoscaling_target_value

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}

resource "aws_wafv2_ip_set" "ireland_ie_ips" {
  name               = "${local.environment_name}-${local.project_name}-ip-set"
  description        = "IPs"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  addresses          = ["161.35.72.212/32",
                        "46.101.124.44/32",
                        "46.101.116.160/32",
                        "85.208.98.128/25",
                        "164.90.168.210/32",
                        "176.58.117.51/32",
                        "80.85.87.84/32",
                        "88.80.184.34/32",
                        "178.79.136.28/32"]
}


resource "aws_wafv2_ip_set" "ireland_ie_ips_cloudfront" {
  name               = "${local.environment_name}-${local.project_name}-ip-set-cloudfront"
  description        = "IPs"
  provider                  = aws.virginia
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = ["161.35.72.212/32",
                        "46.101.124.44/32",
                        "46.101.116.160/32",
                        "85.208.98.128/25",
                        "164.90.168.210/32",
                        "176.58.117.51/32",
                        "80.85.87.84/32",
                        "88.80.184.34/32",
                        "178.79.136.28/32"]
}


resource "aws_wafv2_web_acl" "ireland_ie_waf_cloudfront" {
  name  = "${local.project_name}-waf-cloudfront"
  provider                  = aws.virginia
  scope = "CLOUDFRONT"

  default_action {
    allow {}
  }

  rule {
    name     = "AWSRateBasedRuleDomesticDOS"
    priority = 1

    action {
      captcha {}
    }

    statement {
      rate_based_statement {
        limit              = 300
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSRateBasedRuleDomesticDOS"
      sampled_requests_enabled   = true
    }
  }
  rule {
    name     = "AWS-AWSManagedRulesBotControlRuleSet"
    priority = 0
    override_action {
      none {
      }
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesBotControlRuleSet"
        vendor_name = "AWS"
        scope_down_statement {
            not_statement {
              statement {
                ip_set_reference_statement { 
                  arn = aws_wafv2_ip_set.ireland_ie_ips_cloudfront.arn
                }
               }
            }
        }  
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesBotControlRuleSet"
      sampled_requests_enabled   = true
    }
  }
  
  rule {
    name     = "AWS-AWSManagedRulesAmazonIpReputationList"
    priority = 2
    override_action {
      none {
      }
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesAmazonIpReputationList"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesAnonymousIpList"
    priority = 3
    override_action {
      none {
      }
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAnonymousIpList"
        vendor_name = "AWS"

        rule_action_override {
          action_to_use {
            allow {}
          }

          name = "HostingProviderIPList"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesAnonymousIpList"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 4
    override_action {
      none {
      }
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesUnixRuleSet"
    priority = 5
    override_action {
      none {
      }
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesUnixRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesUnixRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesWindowsRuleSet"
    priority = 6
    override_action {
      none {
      }
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesWindowsRuleSet"
        vendor_name = "AWS"
        rule_action_override {
          action_to_use {
            allow {}
          }

          name = "WindowsShellCommands_BODY"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesWindowsRuleSet"
      sampled_requests_enabled   = true
    }
  }
    rule {
    name     = "AWS-AWSManagedRulesSQLiRuleSet"
    priority = 7
    override_action {
      none {
      }
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
        rule_action_override {
          action_to_use {
            allow {}
          }

          name = "AWSManagedRulesSQLiRuleSet_BODY"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${local.project_name}-waf-metrics"
    sampled_requests_enabled   = true
  }
}


resource "aws_cloudwatch_log_group" "example" {
  provider = aws.virginia
  name = "aws-waf-logs-ireland-ie"
}

resource "aws_wafv2_web_acl_logging_configuration" "example" {
  provider = aws.virginia
  log_destination_configs = [aws_cloudwatch_log_group.example.arn]
  resource_arn            = aws_wafv2_web_acl.ireland_ie_waf_cloudfront.arn
}

resource "aws_cloudwatch_log_resource_policy" "example" {
  policy_document = data.aws_iam_policy_document.example.json
  policy_name     = "webacl-policy-uniq-name"
}

data "aws_iam_policy_document" "example" {
  version = "2012-10-17"
  statement {
    effect = "Allow"
    principals {
      identifiers = ["delivery.logs.amazonaws.com"]
      type        = "Service"
    }
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.example.arn}:*"]
    condition {
      test     = "ArnLike"
      values   = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
      variable = "aws:SourceArn"
    }
    condition {
      test     = "StringEquals"
      values   = [tostring(data.aws_caller_identity.current.account_id)]
      variable = "aws:SourceAccount"
    }
  }
}

data "aws_region" "current" {}


# ------------------------------------------------
# CloudFront Static Files and Assets
# ------------------------------------------------

locals {
  cloudfront_s3_origin_id = "AssetsS3Origin"
}


resource "aws_cloudfront_distribution" "dynamic" {
  web_acl_id    = aws_wafv2_web_acl.ireland_ie_waf_cloudfront.arn
  origin {
    domain_name = aws_lb.public_sites.dns_name
    origin_id   = aws_lb.public_sites.name

    custom_origin_config {
      origin_read_timeout      = 60
      origin_keepalive_timeout = 60
      http_port                = 80
      https_port               = 443
      origin_protocol_policy   = "https-only"
      origin_ssl_protocols     = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }
  enabled = true
  comment = "Website and CMS Assets Distribution."
  aliases = ["www.${local.domain_ireland_ie}"]

  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.cf-logs.bucket_domain_name
    prefix          = "${local.domain_ireland_ie}-cloudfront"
  }
  ordered_cache_behavior {
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = aws_lb.public_sites.name

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc"
    viewer_protocol_policy   = "allow-all"
    path_pattern             = "/search/*"
  } 
  ordered_cache_behavior {
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = aws_lb.public_sites.name

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc"
    viewer_protocol_policy   = "allow-all"
    path_pattern             = "/overseas-travel/advice/*"
  } 

  ordered_cache_behavior {
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = aws_lb.public_sites.name

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc"
    viewer_protocol_policy   = "allow-all"
    path_pattern             = "*/news-archive/"
  } 


  ordered_cache_behavior {
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = aws_lb.public_sites.name

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc"
    viewer_protocol_policy   = "allow-all"
    path_pattern             = "*/news-and-events/"
  } 


  ordered_cache_behavior {
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = aws_lb.public_sites.name

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc"
    viewer_protocol_policy   = "allow-all"
    path_pattern             = "*/annual-reports/"
  } 

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = aws_lb.public_sites.name

    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc"
    cache_policy_id          = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    viewer_protocol_policy   = "allow-all"
    min_ttl                  = 0
    default_ttl              = 3600
    max_ttl                  = 86400

    response_headers_policy_id = aws_cloudfront_response_headers_policy.assets_cors.id
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn            = aws_acm_certificate.dynamic_cert.arn
    ssl_support_method             = "sni-only"
    minimum_protocol_version       = "TLSv1.2_2021"
    cloudfront_default_certificate = false
  }

  depends_on = [
    aws_acm_certificate.dynamic_cert
  ]
}


resource "aws_acm_certificate" "dynamic_cert" {
  domain_name               = "www.${local.domain_ireland_ie}"
  validation_method         = "DNS"
  provider                  = aws.virginia

  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_acm_certificate" "assets_cert" {
  domain_name               = "assets.${local.domain_ireland_ie}"
  validation_method         = "DNS"
  provider                  = aws.virginia

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_cloudfront_origin_access_control" "assets" {
  name                              = "static-assets"
  description                       = "Frontend Static Files."
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_response_headers_policy" "assets_cors" {
  name    = "website-cors"
  comment = "CORS configuration for the assets distribution to allow the website and CMS to access it."

  cors_config {
    access_control_allow_credentials = false

    access_control_allow_headers {
      items = ["*"]
    }

    access_control_allow_methods {
      items = ["GET"]
    }

    access_control_allow_origins {
      items = [local.domain_ireland_ie, "content.${local.domain_ireland_ie}", "www.${local.domain_ireland_ie}"]
    }

    origin_override = true
  }
}

resource "aws_cloudfront_distribution" "assets" {
  origin {
    domain_name              = aws_s3_bucket.assets.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.assets.id
    origin_id                = local.cloudfront_s3_origin_id
  }

  enabled = true
  comment = "Website and CMS Assets Distribution."
  aliases = ["assets.${local.domain_ireland_ie}"]

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.cloudfront_s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400

    response_headers_policy_id = aws_cloudfront_response_headers_policy.assets_cors.id
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn            = aws_acm_certificate.assets_cert.arn
    ssl_support_method             = "sni-only"
    minimum_protocol_version       = "TLSv1.2_2021"
    cloudfront_default_certificate = false
  }

  depends_on = [
    aws_acm_certificate.assets_cert
  ]
}

data "aws_iam_policy_document" "cloudfront_assets_access" {
  statement {
    actions = [ "s3:GetObject" ]
    resources = [ "${aws_s3_bucket.assets.arn}/*" ]

    principals {
      type = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test = "StringEquals"
      variable = "AWS:SourceArn"
      values = [aws_cloudfront_distribution.assets.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "assets" {
  bucket = aws_s3_bucket.assets.id
  policy = data.aws_iam_policy_document.cloudfront_assets_access.json
}
