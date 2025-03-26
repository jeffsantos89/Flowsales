variable "aws_region" {
  type        = string
  description = "The AWS region where resources will be created."
  default     = "us-east-1"
  validation {
    condition     = can(regex("^us\\-east\\-[1-2]$", var.aws_region))
    error_message = "The AWS region must be 'us-east-1' or 'us-east-2'."
  }
}

variable "aws_profile" {
  type        = string
  description = "The AWS CLI profile to use for authentication."
  default     = "default"
  validation {
    condition     = length(var.aws_profile) > 0
    error_message = "The AWS profile name must not be empty."
  }
}

variable "cluster_name" {
  type        = string
  description = "The name of the EKS cluster."
  default     = "flowsale-eks"
  validation {
    condition     = length(var.cluster_name) > 0 && length(var.cluster_name) <= 100
    error_message = "The cluster name must be between 1 and 100 characters."
  }
}

variable "environment" {
  type        = string
  description = "The environment for the deployment (e.g., dev, staging, prod)."
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "The environment must be one of 'dev', 'staging', or 'prod'."
  }
}
