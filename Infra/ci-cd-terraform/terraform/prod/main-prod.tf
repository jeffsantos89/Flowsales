terraform {
  required_version = ">= 1.2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.19.0"

  name = "flowsale-vpc"
  cidr = "10.0.0.0/16"

  azs             = slice(data.aws_availability_zones.available.names, 0, 2)
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.3.0/24", "10.0.4.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = {
    Project     = "Flowsale"
    Environment = var.environment
  }
}

data "aws_availability_zones" "available" {}

module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  version         = "19.0.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.25"
  subnets         = module.vpc.private_subnets
  vpc_id          = module.vpc.vpc_id

  enable_irsa = true

  node_groups_defaults = {
    ami_type = "AL2_x86_64"
  }
  node_groups = {
    default = {
      desired_capacity = 2
      max_capacity     = 3
      min_capacity     = 2
      instance_types   = ["t3.medium"]
      key_name         = var.key_name
      additional_security_group_ids = [aws_security_group.eks_node.id]
    }
  }

  tags = {
    Project     = "Flowsale"
    Environment = var.environment
  }
}

resource "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_id
}

resource "aws_security_group" "eks_node" {
  name_prefix = "eks-node-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "eks-node-sg"
    Project     = "Flowsale"
    Environment = var.environment
  }
}

resource "aws_eks_cluster" "example" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids = module.vpc.private_subnets
  }

  encryption_config {
    resources = ["secrets"]
    provider {
      key_arn = aws_kms_key.eks.arn
    }
  }

  tags = {
    Project     = "Flowsale"
    Environment = var.environment
  }
}

resource "aws_kms_key" "eks" {
  description = "KMS key for EKS"
  enable_key_rotation = true

  tags = {
    Project     = "Flowsale"
    Environment = var.environment
  }
}

resource "aws_iam_role" "eks_cluster" {
  name = "eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project     = "Flowsale"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "eks_cluster_AmazonEKSClusterPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_iam_role_policy_attachment" "eks_cluster_AmazonEKSVPCResourceController" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.eks_cluster.name
}
