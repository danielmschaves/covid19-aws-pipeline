variable "AWS_REGION" {
  description = "The AWS region to use"
  default     = "us-east-1"
}

variable "GLUE_ROLE_ARN" {
  description = "The ARN of the IAM role for AWS Glue"
}

variable "GLUE_ROLE_NAME" {
  description = "The name of the IAM role for AWS Glue"
}

variable "S3_BUCKET" {
  description = "The S3 bucket where the Glue scripts are stored"
}

variable "ATHENA_DATABASE" {
  description = "The Athena database name"
}

variable "ATHENA_OUTPUT_BUCKET" {
  description = "The S3 bucket for Athena query results"
}

variable "REDSHIFT_USER" {
  description = "The Redshift username"
}

variable "REDSHIFT_PASSWORD" {
  description = "The Redshift password"
}

variable "REDSHIFT_JDBC_URL" {
  description = "The Redshift JDBC URL"
}

variable "REDSHIFT_DATABASE" {
  description = "The Redshift database name"
}

variable "REDSHIFT_SCHEMA" {
  description = "The Redshift schema name"
}
