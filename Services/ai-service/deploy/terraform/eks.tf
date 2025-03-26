# ===================== #
#       MÓDULO EKS      #
# ===================== #
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0" # Especificando a versão do módulo

  cluster_name                   = var.cluster_name
  cluster_version               = var.cluster_version
  cluster_endpoint_public_access = true
  cluster_endpoint_private_access = true

  vpc_id     = var.vpc_id
  subnet_ids = var.subnet_ids

  enable_irsa = true # Habilita IAM Roles for Service Accounts

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  # EKS Managed Node Group
  eks_managed_node_groups = {
    main = {
      min_size     = var.min_capacity
      max_size     = var.max_capacity
      desired_size = var.desired_capacity

      instance_types = var.instance_types
      capacity_type  = var.capacity_type

      disk_size = 50

      labels = {
        Environment = var.environment
        Team        = var.team
        Managed-By  = "terraform"
      }

      tags = merge(var.tags, {
        "k8s.io/cluster-autoscaler/enabled" = "true"
        "k8s.io/cluster-autoscaler/${var.cluster_name}" = "owned"
      })

      update_config = {
        max_unavailable_percentage = 33
      }
    }
  }

  # RBAC
  manage_aws_auth_configmap = true
  aws_auth_roles = concat([
    {
      rolearn  = aws_iam_role.eks_admin_role.arn
      username = "admin"
      groups   = ["system:masters"]
    }
  ], var.additional_aws_auth_roles)

  aws_auth_users = concat([
    {
      userarn  = aws_iam_user.eks_user.arn
      username = "eks-user"
      groups   = ["system:masters"]
    }
  ], var.additional_aws_auth_users)

  aws_auth_accounts = map_accounts

  tags = merge(var.tags, {
    Environment = var.environment
    Team        = var.team
    Managed-By  = "terraform"
  })
}

# Cluster Autoscaler IAM Role
resource "aws_iam_role" "cluster_autoscaler" {
  name = "${var.cluster_name}-cluster-autoscaler"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = module.eks.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${module.eks.oidc_provider}:sub": "system:serviceaccount:kube-system:cluster-autoscaler"
          }
        }
      }
    ]
  })

  }
  
  resource "aws_iam_role_policy" "cluster_autoscaler" {
    name = "cluster-autoscaler"
    role = aws_iam_role.cluster_autoscaler.id
  
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "autoscaling:DescribeAutoScalingGroups",
            "autoscaling:DescribeAutoScalingInstances",
            "autoscaling:DescribeTags",
            "autoscaling:SetDesiredCapacity",
            "autoscaling:TerminateInstanceInAutoScalingGroup"
          ]
          Resource = "*"
        }
      ]
    })
}

# Novas variáveis
variable "additional_aws_auth_roles" {
  description = "Additional IAM roles to add to aws-auth configmap"
  type = list(object({
    rolearn  = string
    username = string
    groups   = list(string)
  }))
  default = []
}

variable "additional_aws_auth_users" {
  description = "Additional IAM users to add to aws-auth configmap"
  type = list(object({
    userarn  = string
    username = string
    groups   = list(string)
  }))
  default = []
}

variable "team" {
  description = "Team name for tagging"
  type        = string
  default     = "devops"
}

variable "min_capacity" {
  description = "Minimum size of the EKS managed node group"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum size of the EKS managed node group"
  type        = number
  default     = 5
}

variable "desired_capacity" {
  description = "Desired size of the EKS managed node group"
  type        = number
  default     = 2
}

variable "instance_types" {
  description = "List of instance types for the EKS managed node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "capacity_type" {
  description = "Capacity type for the EKS managed node group"
  type        = string
  default     = "ON_DEMAND"
}

variable "map_accounts" {
  description = "Additional AWS account numbers to add to the aws-auth configmap"
  type        = list(string)
  default     = []
}
