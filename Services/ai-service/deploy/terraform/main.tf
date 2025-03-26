# ===================== #
#    PROVIDER AWS       #
# ===================== #
provider "aws" {
    region = var.aws_region
}

variable "aws_region" {
    description = "AWS region"
    default     = "us-east-1"
}

# ===================== #
#      VPC MODULE       #
# ===================== #
module "vpc" {
    source = "terraform-aws-modules/vpc/aws"
    name   = "ai-service-vpc"
    cidr   = "10.0.0.0/16"

    azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
    private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
    public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

    enable_nat_gateway = true
    single_nat_gateway = false

    tags = {
        Name        = "ai-service-vpc"
        Environment = "production"
    }
}

# ===================== #
#      EKS CLUSTER      #
# ===================== #
module "eks" {
    source          = "terraform-aws-modules/eks/aws"
    cluster_name    = var.cluster_name
    cluster_version = var.cluster_version
    vpc_id          = module.vpc.vpc_id
    subnet_ids      = module.vpc.private_subnets
}

resource "aws_eks_node_group" "eks_nodes" {
    cluster_name    = module.eks.cluster_name
    node_group_name = "eks-nodes"
    node_role_arn   = aws_iam_role.eks_node_role.arn
    subnet_ids      = module.vpc.private_subnets

    scaling_config {
        desired_size = 2
        max_size     = 5
        min_size     = 1
    }

    instance_types = ["t3.medium"]

    remote_access {
        ec2_ssh_key = var.key_name
    }

    tags = {
        Name        = "eks-node-group"
        Environment = "production"
    }
}

# ===================== #
#  SECURITY - IAM ROLE  #
# ===================== #
resource "aws_iam_role" "eks_node_role" {
    name = "eks-node-role"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Principal = {
                    Service = "ec2.amazonaws.com"
                }
                Action = "sts:AssumeRole"
            }
        ]
    })

    }
    
    resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
        policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
        role       = aws_iam_role.eks_node_role.name
    }
    
    resource "aws_iam_role_policy_attachment" "eks_ecr_policy" {
        policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
        role       = aws_iam_role.eks_node_role.name
    }
    
    resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
        policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
        role       = aws_iam_role.eks_node_role.name
}

# ===================== #
#  RDS DATABASE (PG)    #
# ===================== #
resource "aws_secretsmanager_secret" "db_password" {
    name        = "rds-db-password"
    description = "The password for the RDS database"

    tags = {
        Name        = "rds-db-password"
        Environment = "production"
    }
}

resource "aws_secretsmanager_secret_version" "db_password_version" {
    secret_id     = aws_secretsmanager_secret.db_password.id
    secret_string = var.db_password
}

module "rds" {
    source          = "terraform-aws-modules/rds/aws"
    identifier      = "ai-service-db"
    engine          = "postgres"
    engine_version  = "15.3"
    instance_class  = "db.t3.medium"
    allocated_storage = 100
    db_name         = var.db_name
    username        = var.db_username
    password        = aws_secretsmanager_secret_version.db_password_version.secret_string
    vpc_security_group_ids = [module.vpc.default_security_group_id]
    db_subnet_group_name   = module.vpc.database_subnet_group

    tags = {
        Name = var.db_name
    }
}

# ===================== #
#      VARIÁVEIS        #
# ===================== #
variable "cluster_name" {
    description = "Nome do cluster EKS"
    default     = "ai-service-cluster"
}

variable "cluster_version" {
    description = "Versão do Kubernetes no EKS"
    default     = "1.27"
}

variable "db_name" {
    description = "Nome do banco de dados RDS"
    default     = "ai_service_db"
}

variable "db_username" {
    description = "Usuário do banco de dados"
    default     = "admin"
}

variable "db_password" {
    description = "Senha do banco de dados"
    type        = string
    sensitive   = true
}

variable "key_name" {
    description = "Chave SSH para acessar as instâncias"
    type        = string
}

# ===================== #
#      OUTPUTS          #
# ===================== #
output "eks_cluster_id" {
    description = "O ID do cluster EKS"
    value       = module.eks.cluster_id
}

output "rds_endpoint" {
    description = "Endpoint do banco de dados RDS"
    value       = module.rds.endpoint
    sensitive   = true
}
