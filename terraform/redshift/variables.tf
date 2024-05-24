variable "AWS_REGION" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "REDSHIFT_USER" {
  description = "Redshift master username"
  type        = string
}

variable "REDSHIFT_PASSWORD" {
  description = "Redshift master password"
  type        = string
}

variable "REDSHIFT_DBNAME" {
  description = "Redshift database name"
  type        = string
  default     = "covid19_dataset_br"
}

variable "REDSHIFT_SCHEMA" {
  description = "Redshift schema name"
  type        = string
  default     = "gold"
}

variable "SUBNET_IDS" {
  description = "List of subnet IDs for the Redshift subnet group"
  type        = list(string)
}

variable "VPC_ID" {
  description = "VPC ID where Redshift cluster will be deployed"
  type        = string
}
