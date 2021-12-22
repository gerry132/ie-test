terraform {
  required_version = ">=0.13.2"
  required_providers {
    aws         = ">=3.26.0"
  }
}


terraform {
  backend "s3" {
    bucket                      = "ireland-ie-infrastructure"
    key                         = "common-alpine-3-11/terraform.tfstate"
    region                      = "eu-west-1"
    shared_credentials_file     = ".aws/credentials"
    encrypt                     = true
  }
}


provider "aws" {
  profile                     = "default"
  region                      = "eu-west-1"
  shared_credentials_file     = ".aws/credentials"
}


data "aws_caller_identity" "current" {}


locals {
  account_id            = data.aws_caller_identity.current.account_id
  environment_name      = "common-alpine-3-11"
  region                = "eu-west-1"
}

locals {
  ecr_repository_name   = local.environment_name
}


# -----------------------------------------------------------------------------
# ECR
# -----------------------------------------------------------------------------

resource "aws_ecr_repository" "alpine_image" {
  name                 = local.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}


# -----------------------------------------------------------------------------
# Values to fill after running terraform is ran, used for codebuild and secrets
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
  value       = aws_ecr_repository.alpine_image.name
}
