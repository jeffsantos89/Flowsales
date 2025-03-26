resource "kubernetes_config_map" "logging_config" {
    metadata {
        name      = "${var.app_name}-logging-config-${var.environment}"
        namespace = var.namespace
        labels = {
            app         = var.app_name
            environment = var.environment
            component   = "logging"
            managed-by  = "terraform"
        }
        annotations = {
            "description" = "Logging configuration for ${var.app_name}"
            "version"     = var.config_version
        }
    }

    data = {
        "logging.yaml" = templatefile("${path.module}/logging/logging.yaml", {
            log_level     = var.log_level
            environment   = var.environment
            service_name  = var.app_name
        })
        "log4j2.xml"   = templatefile("${path.module}/logging/log4j2.xml", {
            log_level     = var.log_level
            environment   = var.environment
            service_name  = var.app_name
        })
    }

    lifecycle {
        create_before_destroy = true
    }
}

variable "environment" {
    type        = string
    description = "Environment (e.g., dev, staging, prod)"
}

variable "config_version" {
    type        = string
    description = "Version of the logging configuration"
    default     = "1.0.0"
}

variable "log_level" {
    type        = string
    description = "Logging level (DEBUG, INFO, WARN, ERROR)"
    default     = "INFO"
    validation {
        condition     = contains(["DEBUG", "INFO", "WARN", "ERROR"], var.log_level)
        error_message = "Log level must be one of: DEBUG, INFO, WARN, ERROR"
    }
}
