variable "AWS_ACCESS_KEY" {
  description = "AWS access key"
  type        = string
}

variable "AWS_SECRET_KEY" {
  description = "AWS secret key"
  type        = string
}

variable "AWS_REGION" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "AWS_ACCOUNT_ID" {
  description = "AWS account ID"
  type        = string
}

variable "S3_BUCKET" {
  description = "S3 bucket name"
  type        = string
}
