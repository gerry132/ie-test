terraform {
  required_version = ">=1.1"
  required_providers {
    aws         = ">=4.0.0"
    random      = ">=3.1.0"
    template    = ">=2.2.0"
  }
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
  project_name                  = "ireland-ie"
  region                        = "eu-west-1"
  # DB
  db_instance_class             = "db.m6g.large"
  # CACHE
  cache_instance_class          = "cache.t3.medium"
  # ECS
  ecr_repository_name           = "${local.environment_name}-${local.project_name}"
  autoscaling_max_capacity      = 6
  autoscaling_min_capacity      = 1
  autoscaling_target_value      = 60
  service_contrainer_port       = 8000
  task_cpu                      = 1024  # min 1024
  task_memory                   = 2048  # min 2048
  # APP
  health_check_path             = "/health-check/"
  SETTINGS_DEBUG                = 0
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
    rachel_dev = {
      description = "Rachel Mannion - OGCIO"
      cidr_blocks = ["139.162.182.140/32"]
    },
    reinaldo_dev = {
      description = "Reinaldo Sanches - OGCIO"
      cidr_blocks = ["172.105.95.186/32", "89.101.167.251/32"]
    },
    keith_po = {
      description = "Keith Costello - OGCIO"
      cidr_blocks = ["37.228.203.132/32"]
    },
    gerry_dev = {
      description = "Gerry Mcbride - OGCIO"
      cidr_blocks = ["52.49.120.79/32", "37.228.234.245/32"]
    },
    kleverson_dev = {
      description = "Kleverson Morais - OGCIO"
      cidr_blocks = ["176.61.106.140/32"]
    },
    nick_dev = {
      description = "Nick Moreton - Torchbox"
      cidr_blocks = ["217.35.72.151/32"]
    },
    mel_dev = {
      description = "Melissa Joy - Torchbox"
      cidr_blocks = ["78.32.251.194/32", "82.16.132.142/32"]
    },
    jane_dev = {
      description = "Jane Hughes - Torchbox"
      cidr_blocks = ["82.5.195.241/32"]
    },
    chris_dev = {
      description = "Chris Shaw - Torchbox"
      cidr_blocks = ["81.106.63.209/32"]
    }
  }
}

# -----------------------------------------------------------------------------
# Values to fill after running terraform is ran, used for codebuild and secrets
# -----------------------------------------------------------------------------

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
  target_id        = aws_lb.default.arn
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
    matcher                 = 200
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
    matcher                 = 200
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

data "aws_acm_certificate" "ireland_ie_import" {
    domain = "www.ireland.ie"
}


resource "aws_acm_certificate" "project" {
  domain_name                 = local.project_domain
  validation_method           = "DNS"

  lifecycle {
    create_before_destroy   = true
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
  certificate_arn       = aws_acm_certificate.project.arn

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

resource "aws_lb_listener_rule" "ireland_ie_443" {
  listener_arn    = aws_lb_listener.public_sites_443.arn
  priority        = 4

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


# -----------------------------------------------------------------------------
# Listener certificates
# -----------------------------------------------------------------------------

resource "aws_lb_listener_certificate" "ireland_ie_certificate" {
  listener_arn    = aws_lb_listener.public_sites_443.arn
  certificate_arn = data.aws_acm_certificate.ireland_ie_import.arn
}

resource "aws_lb_listener_certificate" "admin_ireland_ie_certificate" {
  listener_arn    = aws_lb_listener.project_443.arn
  certificate_arn = aws_acm_certificate.project.arn
}


# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

# Random db password

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
  SETTINGS_AWS_STATIC_BUCKET_NAME   = aws_s3_bucket.assets.id
  SETTINGS_BASE_URL                 = "https://${local.project_domain}"
  SETTINGS_CACHE_ADDRESS            = local.cache_address
  SETTINGS_DATABASE_URL             = local.db_master_url
  SETTINGS_SECRET_KEY               = data.aws_ssm_parameter.random_secret_key.value
  SETTINGS_CORS_ALLOWED_ORIGINS     = "${local.SETTINGS_BASE_URL},https://www.${local.project_domain}"
  SETTINGS_CORS_ALLOW_ALL_ORIGINS   = 0
  SETTINGS_EMAIL_HOST               = "email.${local.region}.amazonaws.com"
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
    SETTINGS_USE_CACHE                  = local.SETTINGS_USE_CACHE
    SETTINGS_USE_S3                     = local.SETTINGS_USE_S3
    SETTINGS_CORS_ALLOWED_ORIGINS       = local.SETTINGS_CORS_ALLOWED_ORIGINS
    SETTINGS_CORS_ALLOW_ALL_ORIGINS     = local.SETTINGS_CORS_ALLOW_ALL_ORIGINS
    SETTINGS_EMAIL_HOST                 = local.SETTINGS_EMAIL_HOST
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
