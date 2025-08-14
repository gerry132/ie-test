variable "environment_name" {}
variable "task_cpu" {}
variable "region" { default = "eu-west-1" }
variable "task_memory" {}
variable "subnets" {}
variable "ecs_security_groups" {}
variable "lb_security_groups" {}
variable "container_definitions" {}
variable "cluster" {}
variable "execution_role" {}
variable "api_domain" {}
variable "vpc_id" {}
variable "project_name" {
  
}
variable "lb_target_group" {
  
}