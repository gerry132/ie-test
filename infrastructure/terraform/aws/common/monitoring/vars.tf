variable "canary_code_s3_bucket" {
  type        = string
  description = "S3 bucket containing the uploaded canary zip"
}

variable "canary_code_s3_key" {
  type        = string
  description = "S3 key for the uploaded canary zip (e.g. canaries/canary-123.zip)"
}

variable "environment_name" {
  
}