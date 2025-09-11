terraform {
  required_version = ">=1.1"
  required_providers {
    aws         = "5.40.0"
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
    bucket                      = "ireland-ie-infrastructure"
    key                         = "uat/terraform.tfstate"
    region                      = "eu-west-1"
    encrypt                     = true
  }
}

data "aws_caller_identity" "current" {}

data "aws_elb_service_account" "elb" {}

data "aws_ssm_parameter" "master_url" {
  name = "master_url"
}

locals {
    db_master_url   = data.aws_ssm_parameter.master_url.value
}


locals {
  account_id                    = data.aws_caller_identity.current.account_id
  elb_account_arn               = data.aws_elb_service_account.elb.arn
  environment_name              = "uat"
  app_aws_username              = "UAT_APP_USER"
  project_domain                = "content.uat.ireland.ie"
  domain_ireland_ie             = "uat.ireland.ie"
  api_domain                    = "https://api.uat.ireland.ie"
  api_domain_plain              = "api.uat.ireland.ie"
  africa_day_domain             = "africaday.uat.ireland.ie"
  project_name                  = "g2g"
  region                        = "eu-west-1"
  # DB
  db_instance_class             = "db.m6g.large"

  # CACHE
  cache_instance_class          = "cache.t3.medium"
  # ECS
  ecr_repository_name           = "${local.environment_name}-${local.project_name}"
  autoscaling_max_capacity      = 2
  autoscaling_min_capacity      = 1
  autoscaling_target_value      = 60
  service_contrainer_port       = 8000
  task_cpu                      = 2048  # min 1024
  task_memory                   = 4096  # min 2048
  # APP
  health_check_path             = "/health-check/"
  SETTINGS_DEBUG                = 0
  SETTINGS_DEBUG_TOOLBAR        = 0
  SETTINGS_USE_S3               = 1
  SETTINGS_USE_CACHE            = 1
  gov_network_cird_blocks       = [
    "169.254.192.0/18",
    "137.191.224.0/19",
    "37.228.225.101/32", # gerry
    "193.178.64.0/19",
    "193.178.96.0/20",
    "139.162.239.108/32",
    "137.191.233.222/32" # browserstack

  ]
  non_gov_network_cird_blocks   = {
    dfa_main = {
      description = "DFA main IP address"
      cidr_blocks = ["62.23.128.137/32"]
    },
    reinaldo_dev = {
      description = "Reinaldo Sanches - OGCIO"
      cidr_blocks = ["172.105.95.186/32", "89.101.167.251/32"]
    },
    gerry_dev = {
      description = "Gerry Mcbride - OGCIO"
      cidr_blocks = ["95.44.14.48/32", "37.228.234.184/32"]
    },
    fergal_dev = {
      description = "Fergal - OGCIO"
      cidr_blocks = ["51.182.250.11/32"]
    },
    deekshana_dev = {
      description = "Deekshana - Sidero"
      cidr_blocks  = ["51.183.41.207/32"]
    },

    sina_dev = {
      description = "Sina - Sidero"
      cidr_blocks  = ["31.53.148.201/32"]
    },
    joe_dev = {
      description = "Joe D - Sidero"
      cidr_blocks  = ["54.195.145.43/32"]
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
  value       = aws_cloudfront_distribution.dynamic.id

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

resource "aws_security_group" "example" {

  vpc_id  = module.network.vpc_id

  ingress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"

    cidr_blocks = [
      "0.0.0.0/0"
    ]
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
# -----------------------------------------------------------------------------
# Security group rules
# -----------------------------------------------------------------------------

# Public access rules

resource "aws_security_group_rule" "internet_to_lb_80" {
  for_each = local.non_gov_network_cird_blocks
  type                      = "ingress"
  from_port                 = 80
  to_port                   = 80
  protocol                  = "tcp"
  security_group_id         = aws_security_group.lb.id
  cidr_blocks               = each.value.cidr_blocks
}


resource "aws_security_group_rule" "internet_to_lb_443" {
  type                      = "ingress"
  from_port                 = 443
  to_port                   = 443
  protocol                  = "tcp"
  security_group_id         = aws_security_group.lb.id
  cidr_blocks               = ["0.0.0.0/0"]
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

resource "aws_s3_bucket" "cf-logs" {
  bucket  = "${local.environment_name}-${local.project_name}-cf-logs"
}

resource "aws_s3_bucket_ownership_controls" "cf-controls" {
  bucket = aws_s3_bucket.cf-logs.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket" "assets" {
  bucket  = "${local.environment_name}-${local.project_name}-assets"
}

resource "aws_s3_bucket_cors_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT"]
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
  name            = "${local.environment_name}-${local.project_name}-front-network-lb-http"
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
  name            = "${local.environment_name}-${local.project_name}-front-network-lb"
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

#resource "aws_acm_certificate" "project" {
#  domain_name                 = local.project_domain
#  subject_alternative_names   = ["www.${local.project_domain}"]
#  validation_method           = "DNS"

#  lifecycle {
#    create_before_destroy   = true
#  }
#}

#resource "aws_acm_certificate" "ireland_ie_ssl" {
#  domain_name                 = "ireland.testing.gov.ie"
#  subject_alternative_names   = ["www.ireland.testing.gov.ie"]
#  validation_method           = "DNS"

 # lifecycle {
  #  create_before_destroy   = true
  #}
#}


resource "aws_acm_certificate" "ireland_ie_content" {
  domain_name                 = "uat.ireland.ie"
  subject_alternative_names = [
     "www.uat.ireland.ie"
  ]
  validation_method           = "DNS"

  lifecycle {
    create_before_destroy   = true
  }
}

resource "aws_acm_certificate" "ireland_ie_content_admin" {
  domain_name                 = "content.uat.ireland.ie"
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
  ssl_policy            = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn       = aws_acm_certificate.ireland_ie_content.arn

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      status_code  = 503
    }
  }
}

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
  ssl_policy            = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn       = aws_acm_certificate.ireland_ie_content.arn

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
  priority        = 2

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
  priority        = 3

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
  priority        = 4

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

#
# Public facing site rule

resource "aws_lb_listener_rule" "ireland_ie_443" {
  listener_arn    = aws_lb_listener.public_sites_443.arn
  priority        = 8

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
  certificate_arn = aws_acm_certificate.ireland_ie_content.arn
}

resource "aws_lb_listener_certificate" "admin_ireland_ie_certificate" {
  listener_arn    = aws_lb_listener.project_443.arn
  certificate_arn = aws_acm_certificate.ireland_ie_content_admin.arn
}

resource "aws_lb_listener_certificate" "africa_day_certificate" {
    listener_arn    = aws_lb_listener.public_sites_443.arn
    certificate_arn = aws_acm_certificate.africa_day.arn
}

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

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
      instance_type = "t3.small.search"
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
  vpc_options {
    subnet_ids = module.network.private_subnet_ids
    security_group_ids = [aws_security_group.example.id]
  }
  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
  advanced_security_options {
      enabled                        = false
      internal_user_database_enabled = true
      master_user_options {
          master_user_arn = aws_iam_user.opensearch.arn
      }
    }
    access_policies = jsonencode(
      {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          aws_iam_user.opensearch.arn,
          aws_iam_user.default.arn
        ]
      },
      "Action": [
        "es:*"
      ],
    }
  ]
}
)
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

resource "aws_cloudwatch_log_group" "ecs_index" {
  name                = "/ecs/${local.environment_name}-index"
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
        "s3:PutObjectTagging",
        "s3:GetObject",
        "s3:GetObjectAcl",
        "s3:DeleteObject",
        "s3:ListBucketMultipartUploads",
        "s3:ListBucketVersions",
        "s3:ListMultipartUploadParts"
      ],
      "Resource": "arn:aws:s3:::${aws_s3_bucket.assets.bucket}/*"
    }
  ]
}
EOF
}


resource "aws_iam_user" "opensearch" {
  name = "opensearch_${local.app_aws_username}"
}

resource "aws_iam_access_key" "opensearch" {
  user = aws_iam_user.opensearch.name
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
  SETTINGS_CLOUDFRONT_ID            = aws_ssm_parameter.CLOUDFRONT_ID.value
  SETTINGS_ALLOWED_HOSTS            = join(", ", ["*"])
  SETTINGS_AWS_ACCESS_KEY_ID        = aws_ssm_parameter.AWS_ACCESS_KEY_ID.value
  SETTINGS_AWS_SECRET_ACCESS_KEY    = aws_ssm_parameter.AWS_SECRET_ACCESS_KEY.value
  SETTINGS_OPENSEARCH_SECRET        = aws_ssm_parameter.OPENSEARCH_SECRET.value
  SETTINGS_OPENSEARCH_ENDPOINT      = aws_ssm_parameter.OPENSEARCH_ENDPOINT.value
  SETTINGS_OPENSEARCH_KEY           = aws_ssm_parameter.OPENSEARCH_KEY.value
  SETTINGS_AWS_STATIC_BUCKET_NAME   = aws_s3_bucket.assets.id
  SETTINGS_BASE_URL                 = "http://www.${local.project_domain}"
  SETTINGS_CACHE_ADDRESS            = local.cache_address
  SETTINGS_DATABASE_URL             = local.db_master_url
  SETTINGS_SECRET_KEY               = data.aws_ssm_parameter.random_secret_key.value
  SETTINGS_CORS_ALLOWED_ORIGINS     = "${local.SETTINGS_BASE_URL},https://api.${local.domain_ireland_ie},https://www.${local.domain_ireland_ie}"
  SETTINGS_CORS_ALLOW_ALL_ORIGINS   = 0
  SETTINGS_EMAIL_HOST               = "email.${local.region}.amazonaws.com"
  SETTINGS_DEFAULT_FROM_EMAIL       = aws_ssm_parameter.DEFAULT_FROM_EMAIL.value

}


data "template_file" "index_task_definition" {
  template    = file("../common/templates/update-indexes-task-definition.tpl")

  vars = {
    ecr_image_url                       = "${local.account_id}.dkr.ecr.eu-west-1.amazonaws.com/${aws_ecr_repository.project_app.name}"
    log_group                           = aws_cloudwatch_log_group.ecs_index.name
    SETTINGS_CLOUDFRONT_ID              = local.SETTINGS_CLOUDFRONT_ID
    name                                = "${local.environment_name}-index"
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
    SETTINGS_BASE_URL                   = local.SETTINGS_BASE_URL
    SETTINGS_DATABASE_URL               = local.SETTINGS_DATABASE_URL
    SETTINGS_SECRET_KEY                 = local.SETTINGS_SECRET_KEY
    SETTINGS_OPENSEARCH_KEY             = local.SETTINGS_OPENSEARCH_KEY
    SETTINGS_OPENSEARCH_SECRET          = local.SETTINGS_OPENSEARCH_SECRET
    SETTINGS_OPENSEARCH_ENDPOINT        = local.SETTINGS_OPENSEARCH_ENDPOINT
    SETTINGS_CORS_ALLOWED_ORIGINS       = local.SETTINGS_CORS_ALLOWED_ORIGINS
  }
}

data "template_file" "task_definition" {
  template    = file("../common/templates/task_definition.tpl")

  vars = {
    ecr_image_url                       = "${local.account_id}.dkr.ecr.eu-west-1.amazonaws.com/${aws_ecr_repository.project_app.name}"
    log_group                           = aws_cloudwatch_log_group.ecs.name
    name                                = "${local.environment_name}-${local.project_name}"
    api_domain                          = local.api_domain
    port                                = local.service_contrainer_port
    region                              = local.region
    task_cpu                            = local.task_cpu
    SETTINGS_CLOUDFRONT_ID              = local.SETTINGS_CLOUDFRONT_ID
    task_memory                         = local.task_memory
    assets_url                          = "assets.${local.domain_ireland_ie}"
    assets_s3_bucket                    = aws_s3_bucket.assets.id

    SETTINGS_ALLOWED_HOSTS              = local.SETTINGS_ALLOWED_HOSTS
    SETTINGS_AWS_ACCESS_KEY_ID          = local.SETTINGS_AWS_ACCESS_KEY_ID
    SETTINGS_AWS_SECRET_ACCESS_KEY      = local.SETTINGS_AWS_SECRET_ACCESS_KEY
    SETTINGS_AWS_STATIC_BUCKET_NAME     = local.SETTINGS_AWS_STATIC_BUCKET_NAME
    SETTINGS_BASE_URL                   = local.SETTINGS_BASE_URL
    SETTINGS_CACHE_ADDRESS              = local.SETTINGS_CACHE_ADDRESS
    SETTINGS_DATABASE_URL               = local.SETTINGS_DATABASE_URL
    SETTINGS_DEBUG                      = local.SETTINGS_DEBUG
    SETTINGS_DEBUG_TOOLBAR              = local.SETTINGS_DEBUG_TOOLBAR
    SETTINGS_SECRET_KEY                 = local.SETTINGS_SECRET_KEY
    SETTINGS_OPENSEARCH_KEY             = local.SETTINGS_OPENSEARCH_KEY
    SETTINGS_OPENSEARCH_SECRET          = local.SETTINGS_OPENSEARCH_SECRET
    SETTINGS_OPENSEARCH_ENDPOINT        = local.SETTINGS_OPENSEARCH_ENDPOINT
    SETTINGS_USE_CACHE                  = local.SETTINGS_USE_CACHE
    SETTINGS_USE_S3                     = local.SETTINGS_USE_S3
    SETTINGS_CORS_ALLOWED_ORIGINS       = local.SETTINGS_CORS_ALLOWED_ORIGINS
    SETTINGS_CORS_ALLOW_ALL_ORIGINS     = local.SETTINGS_CORS_ALLOW_ALL_ORIGINS
    SETTINGS_EMAIL_HOST                 = local.SETTINGS_EMAIL_HOST
    SETTINGS_DEFAULT_FROM_EMAIL         = local.SETTINGS_DEFAULT_FROM_EMAIL
  }
}

module "main_task_definition" {
  source = "../common/task_definition"

  account_id              = local.account_id
  project_name            = local.project_name
  environment_name        = local.environment_name
  assets_s3_bucket        = aws_s3_bucket.assets.id
  log_group               = aws_cloudwatch_log_group.ecs.name
  ecr_image_url           = "${local.account_id}.dkr.ecr.eu-west-1.amazonaws.com/${aws_ecr_repository.project_app.name}"
  cache_address           = local.cache_address
  region                  = local.region
  task_cpu                = local.task_cpu
  task_memory             = local.task_memory
  domain_ireland_ie       = local.domain_ireland_ie
  service_contrainer_port = 8000

  SETTINGS_DEBUG               = local.SETTINGS_DEBUG
  SETTINGS_DEBUG_TOOLBAR       = local.SETTINGS_DEBUG_TOOLBAR
  SETTINGS_EMAIL_HOST          = local.SETTINGS_EMAIL_HOST
  SETTINGS_DEFAULT_FROM_EMAIL  = local.SETTINGS_DEFAULT_FROM_EMAIL
  SETTINGS_CORS_ALLOW_ALL_ORIGINS = local.SETTINGS_CORS_ALLOW_ALL_ORIGINS

  SETTINGS_ALLOWED_HOSTS       = local.SETTINGS_ALLOWED_HOSTS
  SETTINGS_USE_CACHE           = local.SETTINGS_USE_CACHE
  SETTINGS_USE_S3              = local.SETTINGS_USE_S3
  SETTINGS_CLOUDFRONT_ID       = local.SETTINGS_CLOUDFRONT_ID
  SETTINGS_AWS_ACCESS_KEY_ID   = local.SETTINGS_AWS_ACCESS_KEY_ID
  SETTINGS_AWS_SECRET_ACCESS_KEY = local.SETTINGS_AWS_SECRET_ACCESS_KEY
  SETTINGS_AWS_STATIC_BUCKET_NAME = local.SETTINGS_AWS_STATIC_BUCKET_NAME
  SETTINGS_BASE_URL            = local.SETTINGS_BASE_URL
  SETTINGS_DATABASE_URL        = local.SETTINGS_DATABASE_URL
  SETTINGS_SECRET_KEY          = local.SETTINGS_SECRET_KEY
  SETTINGS_OPENSEARCH_KEY      = local.SETTINGS_OPENSEARCH_KEY
  SETTINGS_OPENSEARCH_SECRET   = local.SETTINGS_OPENSEARCH_SECRET
  SETTINGS_OPENSEARCH_ENDPOINT = local.SETTINGS_OPENSEARCH_ENDPOINT
  SETTINGS_CORS_ALLOWED_ORIGINS = local.SETTINGS_CORS_ALLOWED_ORIGINS
}

# Task definition

module "ecs_task_os_index" {
  source = "../common/utils"

  publish_task_definitions = module.main_task_definition.publish_task_definition_rendered
  container_definitions = data.template_file.index_task_definition.rendered
  task_cpu              = "256"
  task_memory           = "512"
  subnets               = module.network.private_subnet_ids
  security_groups       = aws_security_group.ecs.id
  environment_name      = local.environment_name
  cluster               = aws_ecs_cluster.default
  execution_role        = aws_iam_role.task_execution.arn
}

module "api" {
  source = "../common/api"

  container_definitions = module.main_task_definition.container_definitions
  lb_target_group       = aws_lb_target_group.default_admin.arn
  project_name          = local.project_name
  environment_name      = local.environment_name
  task_cpu              = "256"
  task_memory           = "512"
  api_domain            = local.api_domain_plain
  subnets               = module.network.public_subnet_ids
  vpc_id                = module.network.vpc_id
  ecs_security_groups   = aws_security_group.ecs.id
  lb_security_groups    = aws_security_group.lb_gov_network.id
  cluster               = aws_ecs_cluster.default
  execution_role        = aws_iam_role.task_execution.arn
}

resource "aws_ecs_task_definition" "default" {
  family                   = "${local.environment_name}-${local.project_name}"
  execution_role_arn       = aws_iam_role.task_execution.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = local.task_cpu
  memory                   = local.task_memory
  container_definitions    = data.template_file.task_definition.rendered
}

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


##################################
# ORIGINAL CODE ENDS - UNTOUCHED #
##################################

#########################################
### SIDERO MSP MONITORING CODE BEGINS ###
#########################################

### UAT CODE ###

### INSTRUCTIONS FOR SUBSCRIBING TO MONITORING ALERTS ###
# This code may be provided to OGCIO teams to add to add monitoring of uat.reland.ie AWS resources for testing prior to production.
# This will enable monitoring of relevant AWS resources related to www.uat.ireland.ie and will create two new SNS Topics which can be subscribed to.
# SNS Topic Names:
# "high_priority_alert"
# "low_priority_alert"
# You can find SNS from your AWS Console by searching for "SNS"
# How to subscribe email addresses to be notified of alarms:
# https://docs.aws.amazon.com/sns/latest/dg/sns-email-notifications.html
# How to add phone numbers for notification via text message:
# https://docs.aws.amazon.com/sns/latest/dg/sms_manage.html

# The following resources will be deployed and configured:
#	• New Cloudwatch alarms:
#		○ RDS Postgres DB - CPU and Free Strorage Space
#		○ ECS Cluster - CPU and RAM high > 5 mins
#		○ App ELBs - >10 target connection errors within 15 minutes
#		○ ElastiCache - CPU and RAM
#		○ S3 buckets - 4xx and 5xx errors
#########################################################################

### Cloudwatch HIGH - Postgres DB free space - uat-db-postgres ###
resource "aws_cloudwatch_metric_alarm" "uat-db-postgres-free-space-alarm-below-20GB" {
  alarm_name          = "uat-db-postgres-free-space-alarm-below-20GB"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Minimum"
  threshold           = "21474836480"
  alarm_description   = "Alarm when free storage space falls below 20GB"
  dimensions = {
    # Actual DB instance required name below
    DBInstanceIdentifier = "uat-db-postgres"
  }
  tags = {
    "Sidero_MSP" : "true"
  }
}

### Cloudwatch HIGH - Postgres DB CPU Utlization - uat-db-postgres ###
resource "aws_cloudwatch_metric_alarm" "rds-cpu-utilization-above-80percent" {
  alarm_name          = "rds-cpu-utilization-above-80percent"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "3"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Alarm when CPU utilization exceeds 80%"
  dimensions = {
    DBInstanceIdentifier = "uat-db-postgres"
  }
  tags = {
    "Sidero_MSP" : "true"
  }
}

### Cloudwatch HIGH - ECS CPU Utilization - UAT-ireland-ie
resource "aws_cloudwatch_metric_alarm" "ecs-cpu-utilization-above-90percent" {
  alarm_name          = "ecs-cpu-utilization-above-90percent"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "3"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "90"
  alarm_description   = "Alarm when CPU utilization exceeds 90%"
  dimensions = {
    ClusterName = "uat-g2g"
  }
  tags = {
    "Sidero_MSP" : "true"
  }
}

### Cloudwatch HIGH - ECS Memory Utilization - UAT-ireland-ie
resource "aws_cloudwatch_metric_alarm" "ecs-memory-utilization-above-90percent" {
  alarm_name          = "ecs-memory-utilization-above-90percent"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "3"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "90"
  alarm_description   = "Alarm when memory utilization exceeds 90%"
  dimensions = {
    ClusterName = "uat-g2g"
  }
  tags = {
    "Sidero_MSP" : "true"
  }
}

### Cloudwatch LOW - Application ELB Connection Errors - UAT
resource "aws_cloudwatch_metric_alarm" "elb-UAT-alb-multiple-5xx-errors" {
  alarm_name          = "elb-UAT-alb-multiple-5xx-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "3"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "Alarm when the number of HTTP 5XX response codes exceeds 10 for 3 consecutive periods"
  dimensions = {
    LoadBalancer = "app/uat-g2g/3e434df452426d2b"
  }
  tags = {
    "Sidero_MSP" : "true"
  }
}

### Cloudwatch LOW - Network ELB Connection Errors - net-lb
resource "aws_cloudwatch_metric_alarm" "net-lb-connection-multiple-TCP-reset-errors" {
  alarm_name          = "net-lb-connection-multiple-TCP-reset-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "3"
  metric_name         = "TCP_Client_Reset_Count"
  namespace           = "AWS/NetworkELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "Alarm when the number of TCP client reset connections exceeds 10 for 3 consecutive periods"
  dimensions = {
    LoadBalancer = "/net/net-lb/7a66026594941f75"
  }
  tags = {
    "Sidero_MSP" : "true"
  }
}

### Cloudwatch LOW - Elasticache CPU Utilization - redis-uat
resource "aws_cloudwatch_metric_alarm" "elasticache-cpu-above-80percent" {
  alarm_name          = "elasticache-cpu-above-80percent"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Alarm when CPU utilization exceeds 80% for 3 consecutive periods"
  dimensions = {
    CacheClusterId = "redis-uat"
  }
  tags = {
    "Sidero_MSP" : "true"
  }
}

### Cloudwatch LOW - Elasticache Memory Utilization - redis-uat
resource "aws_cloudwatch_metric_alarm" "elasticache-memory-above-8MB" {
  alarm_name          = "elasticache-memory-above-8MB"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "BytesUsedForCache"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "8200000"
  alarm_description   = "Alarm when memory utilization exceeds 8MB for 3 consecutive periods"
  dimensions = {
    CacheClusterId = "redis-uat"
  }
  tags = {
    "Sidero_MSP" : "true"
  }
}

# In UAT we need only test one of each S3 Cloudwatch resource
# We will test for 4xx and 5xx errors on UAT bucket: ireland-ie-infrastructure

### Cloudwatch LOW - S3 4xx_errors - ireland-ie-infrastructure
resource "aws_cloudwatch_metric_alarm" "s3-ireland-ie-infrastructure-4xx-errors-alarm" {
  alarm_name          = "s3-ireland-ie-infrastructure-4xx-errors-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "4xxErrorRate"
  namespace           = "AWS/S3"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "Alarm when 4xx error >10 for 3 consecutive periods"
  dimensions = {
    BucketName = "ireland-ie-infrastructure"
  }
  tags = {
    "Sidero_MSP" : "true"
  }
}

### Cloudwatch LOW - S3 5xx_errors - ireland-ie-infrastructure
resource "aws_cloudwatch_metric_alarm" "s3-ireland-ie-infrastructure-5xx-errors-alarm" {
  alarm_name          = "s3-ireland-ie-infrastructure-5xx-errors-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "5xxErrorRate"
  namespace           = "AWS/S3"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "Alarm when 5xx error rate exceeds >10 for 3 consecutive periods"
  dimensions = {
    BucketName = "ireland-ie-infrastructure"
  }
  tags = {
    "Sidero_MSP" : "true"
  }
}
#############################################################################################

### Create SNS topics - OGCIO may then add emails and phone numbers to these topics #########
## high priority SNS topic
resource "aws_sns_topic" "high_priority_alert" {
  name = "high_priority_alert"
  tags = {
    "Sidero_MSP" : "true"
  }
}
## low priority SNS topic
resource "aws_sns_topic" "low_priority_alert" {
  name = "low_priority_alert"
  tags = {
    "Sidero_MSP" : "true"
  }
}
##############################################################################################

### Eventbridge rules - high_priority_alert (used to be called cloudwatch events) ############
resource "aws_cloudwatch_event_rule" "high_priority_alert" {
  name          = "high_priority_alert"
  description   = "Triggers SNS topic high_priority_alert to alert subscribed users"
  event_pattern = jsonencode({
    "source": ["aws.cloudwatch"],
    "detail-type": ["CloudWatch Alarm State Change"],
    "detail": {
      "state": {
        "value": ["ALARM"]
      }
    },
    "resources": [aws_cloudwatch_metric_alarm.uat-db-postgres-free-space-alarm-below-20GB.arn,
      aws_cloudwatch_metric_alarm.rds-cpu-utilization-above-80percent.arn,
      aws_cloudwatch_metric_alarm.ecs-cpu-utilization-above-90percent.arn,
      aws_cloudwatch_metric_alarm.ecs-memory-utilization-above-90percent.arn
    ]
  })
}

## Define the event target - trigger SNS
resource "aws_cloudwatch_event_target" "high_priority_alert" {
  rule      = aws_cloudwatch_event_rule.high_priority_alert.name
  target_id = "high_priority_alert"
  arn       = aws_sns_topic.high_priority_alert.arn
}

### Applies IAM policy for SNS permissions for high_priority_alert
resource "aws_sns_topic_policy" "sns_topic_policy_high" {
  arn    = aws_sns_topic.high_priority_alert.arn
  policy = data.aws_iam_policy_document.sns_topic_policy_high.json
}

data "aws_iam_policy_document" "sns_topic_policy_high" {
  statement {
    effect  = "Allow"
    actions = ["SNS:Publish"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    resources = [
      aws_sns_topic.high_priority_alert.arn
    ]
  }
}

### Eventbridge rules - low_priority_alert (used to be called cloudwatch events) ############
resource "aws_cloudwatch_event_rule" "low_priority_alert" {
  name          = "low_priority_alert"
  description   = "Triggers SNS topic low_priority_alert to alert subscribed users"
  event_pattern = jsonencode({
    "source": ["aws.cloudwatch"],
    "detail-type": ["CloudWatch Alarm State Change"],
    "detail": {
      "state": {
        "value": ["ALARM"]
      }
    },
    "resources": [aws_cloudwatch_metric_alarm.elb-UAT-alb-multiple-5xx-errors.arn,
      aws_cloudwatch_metric_alarm.net-lb-connection-multiple-TCP-reset-errors.arn,
      aws_cloudwatch_metric_alarm.elasticache-cpu-above-80percent.arn,
      aws_cloudwatch_metric_alarm.elasticache-memory-above-8MB.arn,
      aws_cloudwatch_metric_alarm.s3-ireland-ie-infrastructure-4xx-errors-alarm.arn,
      aws_cloudwatch_metric_alarm.s3-ireland-ie-infrastructure-5xx-errors-alarm.arn
    ]
  })
}

## Define the event target - trigger SNS
resource "aws_cloudwatch_event_target" "low_priority_alert" {
  rule      = aws_cloudwatch_event_rule.low_priority_alert.name
  target_id = "low_priority_alert"
  arn       = aws_sns_topic.low_priority_alert.arn
}

### Applies IAM policy for SNS permissions for low_priority_alert
resource "aws_sns_topic_policy" "sns_topic_policy_low" {
  arn    = aws_sns_topic.low_priority_alert.arn
  policy = data.aws_iam_policy_document.sns_topic_policy_low.json
}

data "aws_iam_policy_document" "sns_topic_policy_low" {
  statement {
    effect  = "Allow"
    actions = ["SNS:Publish"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    resources = [
      aws_sns_topic.low_priority_alert.arn
    ]
  }
}

#######################################
### SIDERO MSP MONITORING CODE ENDS ###
#######################################



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
    path_pattern             = "/en/eu-jobs/"
  }
  ordered_cache_behavior {
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = aws_lb.public_sites.name

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc"
    viewer_protocol_policy   = "allow-all"
    path_pattern             = "*/overseas-travel/advice/*"
  }
  ordered_cache_behavior {
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = aws_lb.public_sites.name

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc"
    viewer_protocol_policy   = "allow-all"
    path_pattern             = "*/publication-index/*"
  }


  ordered_cache_behavior {
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = aws_lb.public_sites.name

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc"
    viewer_protocol_policy   = "allow-all"
    path_pattern             = "*/news-and-events/*"
  }

  ordered_cache_behavior {
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = aws_lb.public_sites.name

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc"
    viewer_protocol_policy   = "allow-all"
    path_pattern             = "*/news-and-speeches/*"
  }

  ordered_cache_behavior {
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = aws_lb.public_sites.name

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc"
    viewer_protocol_policy   = "allow-all"
    path_pattern             = "*/annual-reports/*"
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

resource "aws_wafv2_ip_set" "ireland_ie_ips_cloudfront" {
  name               = "${local.environment_name}-${local.project_name}-ip-set-cloudfront"
  description        = "IPs"
  provider                  = aws.virginia
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = ["161.35.72.212/32",   # ireland_ie_ips
                        "46.101.124.44/32",   # ireland_ie_ips
                        "46.101.116.160/32",  # ireland_ie_ips
                        "85.208.98.128/25",   # ireland_ie_ips
                        "164.90.168.210/32",  # ireland_ie_ips
                        "52.18.199.206/32",
                        "52.209.191.79/32",
                        "176.58.117.51/32",   # ireland_ie_ips
                        "80.85.87.84/32",     # ireland_ie_ips
                        "88.80.184.34/32",    # ireland_ie_ips
                        "178.79.136.28/32",   # ireland_ie_ips

                        "169.254.192.0/18",   # gov_network_cird_blocks
                        "137.191.224.0/19",   # gov_network_cird_blocks
                        "193.178.64.0/19",    # gov_network_cird_blocks
                        "193.178.96.0/20",    # gov_network_cird_blocks
                        "139.162.239.108/32", # gov_network_cird_blocks

                        "31.53.148.201/32",   # Sina
                        "51.183.41.207/32",   # Deekshana
                        "51.182.250.11/32",   # Fergal
                        "62.23.128.137/32",    # DFA
                        "37.228.206.182/32",  # jaikiran_dev
                        ]
}


resource "aws_wafv2_web_acl" "ireland_ie_waf_cloudfront" {
  name  = "${local.project_name}-waf-cloudfront"
  provider                  = aws.virginia
  scope = "CLOUDFRONT"

  default_action {
    block {}
  }
 rule {
    name     = "AllowWhitelistedIPs"
    priority = 1

    action {
      allow {}
    }

    statement {
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.ireland_ie_ips_cloudfront.arn
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "whitelistIPs"
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
      items = ["GET", "PUT"]
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
    actions = [ "s3:GetObject", "s3:PutObject", "s3:PutObjectAcl" ]
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
