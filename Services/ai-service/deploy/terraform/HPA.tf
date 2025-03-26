resource "kubernetes_horizontal_pod_autoscaler_v2" "ai_hpa" {
    metadata {
        name      = "ai-service-hpa"
        namespace = var.namespace
        labels = {
            app     = "ai-service"
            env     = var.environment
            team    = "ai-team"
            version = var.app_version
        }
        annotations = {
            "description" = "HPA for AI Service"
            "owner"       = "platform-team"
        }
    }

    spec {
        scale_target_ref {
            api_version = "apps/v1"
            kind        = "Deployment"
            name        = "ai-service"
        }

        min_replicas = var.hpa_min_replicas
        max_replicas = var.hpa_max_replicas

        # Comportamento de escala personalizado
        behavior {
            scale_down {
                stabilization_window_seconds = 300
                select_policy               = "Max"
                policy {
                    period_seconds = 120
                    type          = "Pods"
                    value         = 1
                }
            }
            scale_up {
                stabilization_window_seconds = 60
                select_policy               = "Max"
                policy {
                    period_seconds = 60
                    type          = "Percent"
                    value         = 100
                }
            }
        }

        metric {
            type = "Resource"
            resource {
                name = "cpu"
                target {
                    type               = "Utilization"
                    average_utilization = var.cpu_threshold
                }
            }
        }

        metric {
            type = "Resource"
            resource {
                name = "memory"
                target {
                    type               = "Utilization"
                    average_utilization = var.memory_threshold
                }
            }
        }

        # Métrica customizada adicional para latência
        metric {
            type = "Pods"
            pods {
                metric {
                    name = "http_request_duration_seconds"
                }
                target {
                    type          = "AverageValue"
                    average_value = "0.1"
                }
            }
        }
    }

    lifecycle {
        ignore_changes = [
            metadata[0].annotations["last_updated"]
        ]
    }
}

# Variáveis necessárias
variable "hpa_min_replicas" {
    type        = number
    default     = 2
    description = "Minimum number of replicas"
}

variable "hpa_max_replicas" {
    type        = number
    default     = 10
    description = "Maximum number of replicas"
}

variable "cpu_threshold" {
    type        = number
    default     = 70
    description = "CPU utilization threshold percentage"
}

variable "memory_threshold" {
    type        = number
    default     = 75
    description = "Memory utilization threshold percentage"
}

variable "environment" {
    type        = string
    description = "Environment name (e.g., prod, staging, dev)"
}

variable "app_version" {
    type        = string
    description = "Application version"
}
