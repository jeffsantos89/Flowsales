# ============================= #
#       PROVIDERS CONFIG        #
# ============================= #

provider "aws" {
  region = var.region

  # Remove aws_profile para evitar dependência de configuração local
  # Essa linha pode ser reativada para ambientes de desenvolvimento.
  # profile = var.aws_profile
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  token                  = data.aws_eks_cluster_auth.cluster.token
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  # Permite fallback para kubeconfig local caso o cluster ainda não tenha sido provisionado
  config_path    = var.use_kubeconfig ? var.kubeconfig_path : null
  config_context = var.use_kubeconfig ? var.kubeconfig_context : null
}

# ============================= #
#      VARIÁVEIS DE CONFIG      #
# ============================= #

variable "region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-west-2"

  validation {
    condition     = contains(["us-west-2", "us-east-1", "eu-west-1"], var.region)
    error_message = "Região inválida. Escolha entre: us-west-2, us-east-1, eu-west-1."
  }
}

variable "use_kubeconfig" {
  description = "If true, use local kubeconfig instead of EKS authentication"
  type        = bool
  default     = false
}

variable "kubeconfig_path" {
  description = "Path to the kubeconfig file (only used if use_kubeconfig=true)"
  type        = string
  default     = "${path.module}/kubeconfig"
}

variable "kubeconfig_context" {
  description = "The name of the kubeconfig context (only used if use_kubeconfig=true)"
  type        = string
  default     = "default"
}

# ============================= #
#   AUTENTICAÇÃO NO CLUSTER EKS #
# ============================= #

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_name
}

module "eks" {
  source = "./modules/eks"
}
