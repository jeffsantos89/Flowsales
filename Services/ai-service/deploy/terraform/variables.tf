# ===========================================
# 📌 VARIÁVEIS (já definidas no seu .tfvars)
# ===========================================

variable "namespace" {
  description = "The namespace in which to deploy the service"
  type        = string
  default     = "ai-service"
  validation {
    condition     = length(var.namespace) > 0
    error_message = "Namespace must not be empty"
  }
}

variable "app_name" {
  description = "The name of the application"
  type        = string
  default     = "ai-service"
  validation {
    condition     = length(var.app_name) > 0
    error_message = "App name must not be empty"
  }
}

variable "service_port" {
  description = "The port on which the service will be exposed"
  type        = number
  default     = 5000
  validation {
    condition     = var.service_port > 0 && var.service_port < 65536
    error_message = "Service port must be between 1 and 65535"
  }
}

variable "target_port" {
  description = "The port on which the application is running"
  type        = number
  default     = 5000
  validation {
    condition     = var.target_port > 0 && var.target_port < 65536
    error_message = "Target port must be between 1 and 65535"
  }
}

variable "service_type" {
  description = "The type of Kubernetes service"
  type        = string
  default     = "ClusterIP"
  validation {
    condition     = contains(["ClusterIP", "NodePort", "LoadBalancer"], var.service_type)
    error_message = "Service type must be one of ClusterIP, NodePort, or LoadBalancer"
  }
}

variable "node_port" {
  description = "The NodePort for accessing the service externally"
  type        = number
  default     = 32000
  validation {
    condition     = var.node_port >= 30000 && var.node_port <= 32767
    error_message = "NodePort must be between 30000 and 32767"
  }
}

variable "db_credentials" {
  description = "Database credentials stored in AWS Secrets Manager"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "The name of the database"
  type        = string
  validation {
    condition     = length(var.db_name) > 0
    error_message = "Database name must not be empty"
  }
}

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
  validation {
    condition     = length(var.vpc_id) > 0
    error_message = "VPC ID must not be empty"
  }
}

variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the database"
  type        = list(string)
  validation {
    condition     = length(var.allowed_cidr_blocks) > 0
    error_message = "Allowed CIDR blocks must not be empty"
  }
}

variable "subnet_ids" {
  description = "Lista de IDs das subnets para o cluster EKS."
  type        = list(string)
  validation {
    condition     = length(var.subnet_ids) > 0
    error_message = "Subnet IDs must not be empty"
  }
}

# ===========================================
# 📌 RECURSO - Serviço Kubernetes para AI
# ===========================================

resource "kubernetes_service" "ai_service" {
  metadata {
    name      = var.app_name
    namespace = var.namespace

    labels = {
      app.kubernetes.io/name       = var.app_name
      app.kubernetes.io/component  = "api"
      app.kubernetes.io/managed-by = "terraform"
      environment                  = var.namespace
    }

    annotations = {
      prometheus.io/scrape = "true"
      prometheus.io/port   = tostring(var.service_port)
    }
  }

  spec {
    selector = {
      app = var.app_name
    }

    port {
      name        = "http"
      port        = var.service_port
      target_port = var.target_port
      node_port   = var.service_type == "NodePort" || var.service_type == "LoadBalancer" ? var.node_port : null
    }

    type = var.service_type
  }
}
