data "template_file" "task_definition" {
  template    = file("../common/templates/task_definition.tpl")

  vars = {
    ecr_image_url                       = var.ecr_image_url
    log_group                           = var.log_group
    name                                = "${var.environment_name}-${var.project_name}"
    port                                = var.service_contrainer_port
    region                              = var.region
    task_cpu                            = var.task_cpu
    SETTINGS_CLOUDFRONT_ID              = var.SETTINGS_CLOUDFRONT_ID
    task_memory                         = var.task_memory
    assets_url                          = "assets.${var.domain_ireland_ie}"
    assets_s3_bucket                    = var.assets_s3_bucket


    SETTINGS_ALLOWED_HOSTS              = var.SETTINGS_ALLOWED_HOSTS
    SETTINGS_AWS_ACCESS_KEY_ID          = var.SETTINGS_AWS_ACCESS_KEY_ID
    SETTINGS_AWS_SECRET_ACCESS_KEY      = var.SETTINGS_AWS_SECRET_ACCESS_KEY
    SETTINGS_AWS_STATIC_BUCKET_NAME     = var.SETTINGS_AWS_STATIC_BUCKET_NAME
    SETTINGS_BASE_URL                   = var.SETTINGS_BASE_URL
    SETTINGS_CACHE_ADDRESS              = var.cache_address
    SETTINGS_DATABASE_URL               = var.SETTINGS_DATABASE_URL
    SETTINGS_DEBUG                      = var.SETTINGS_DEBUG
    SETTINGS_DEBUG_TOOLBAR              = var.SETTINGS_DEBUG_TOOLBAR
    SETTINGS_SECRET_KEY                 = var.SETTINGS_SECRET_KEY
    SETTINGS_OPENSEARCH_KEY             = var.SETTINGS_OPENSEARCH_KEY
    SETTINGS_OPENSEARCH_SECRET          = var.SETTINGS_OPENSEARCH_SECRET
    SETTINGS_OPENSEARCH_ENDPOINT        = var.SETTINGS_OPENSEARCH_ENDPOINT
    SETTINGS_USE_CACHE                  = var.SETTINGS_USE_S3
    SETTINGS_USE_S3                     = var.SETTINGS_USE_CACHE
    SETTINGS_CORS_ALLOWED_ORIGINS       = var.SETTINGS_CORS_ALLOWED_ORIGINS
    SETTINGS_CORS_ALLOW_ALL_ORIGINS     = var.SETTINGS_CORS_ALLOW_ALL_ORIGINS
    SETTINGS_EMAIL_HOST                 = var.SETTINGS_EMAIL_HOST
    SETTINGS_DEFAULT_FROM_EMAIL         = var.SETTINGS_DEFAULT_FROM_EMAIL

  }
}

data "template_file" "publish_task_definition" {
  template    = file("../common/templates/publish_scheduled.tpl")

  vars = {
    ecr_image_url                       = "${local.account_id}.dkr.ecr.eu-west-1.amazonaws.com/${aws_ecr_repository.project_app.name}"
    log_group                           = aws_cloudwatch_log_group.ecs_index.name
    name                                = "${local.environment_name}-publish_scheduled"
    port                                = local.service_contrainer_port
    region                              = local.region
    task_cpu                            = local.task_cpu
    task_memory                         = local.task_memory
    assets_s3_bucket                    = aws_s3_bucket.assets.id

    SETTINGS_ALLOWED_HOSTS              = local.SETTINGS_ALLOWED_HOSTS
    SETTINGS_OPENSEARCH_MASTER          = local.SETTINGS_OPENSEARCH_MASTER
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

variable "cache_address" {

}
variable "SETTINGS_DEBUG_TOOLBAR" {}
variable "SETTINGS_DEBUG" {}
variable "account_id" {}
variable "SETTINGS_CLOUDFRONT_ID" {}
variable "SETTINGS_DEFAULT_FROM_EMAIL" {}
variable "SETTINGS_EMAIL_HOST" {}
variable "SETTINGS_CORS_ALLOW_ALL_ORIGINS" {}
variable "environment_name" {}
variable "service_contrainer_port" {}
variable "region" { default = "eu-west-1" }
variable "task_memory" { default = "512" }
variable "task_cpu" { default = "256" }
variable "assets_s3_bucket" {}
variable "domain_ireland_ie" {}
variable "SETTINGS_ALLOWED_HOSTS" {}
variable "SETTINGS_AWS_ACCESS_KEY_ID" {}
variable "SETTINGS_AWS_SECRET_ACCESS_KEY" {}
variable "SETTINGS_AWS_STATIC_BUCKET_NAME" {}
variable "SETTINGS_BASE_URL" {}
variable "SETTINGS_DATABASE_URL" {}
variable "SETTINGS_CORS_ALLOWED_ORIGINS" {}
variable "SETTINGS_OPENSEARCH_ENDPOINT" {}
variable "SETTINGS_OPENSEARCH_SECRET" {}
variable "SETTINGS_OPENSEARCH_KEY" {}
variable "SETTINGS_USE_CACHE" {}
variable "SETTINGS_USE_S3" {}
variable "SETTINGS_SECRET_KEY" {}
variable "log_group" {

}
variable "ecr_image_url" {

}
variable "project_name" {

}

output "container_definitions" {
    value = data.template_file.task_definition.rendered
}

output "publish_task_definition_rendered" {
  value = data.template_file.publish_task_definition.rendered
}
