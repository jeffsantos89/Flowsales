output "eks_cluster_name" {
  description = "Nome do cluster EKS"
  value       = module.eks != null ? module.eks.cluster_id : ""
}

output "eks_cluster_endpoint" {
  description = "Endpoint do cluster EKS"
  value       = module.eks != null ? module.eks.cluster_endpoint : ""
}

output "eks_cluster_ca" {
  description = "Certificado CA do cluster"
  value       = module.eks != null ? module.eks.cluster_ca_certificate : ""
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc != null ? module.vpc.vpc_id : ""
}

output "tags" {
  description = "Tags comuns para todos os recursos"
  value = {
    Environment = var.environment
    Project     = var.project
    Owner       = var.owner
  }
}
