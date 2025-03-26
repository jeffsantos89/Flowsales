# ========================== #
#      VARIÁVEIS GERAIS      #
# ========================== #
variable "enable_logging" {
    description = "Enable logging for the EKS cluster"
    type        = bool
    default     = true
}

variable "enable_database" {
    description = "Enable the AI service database"
    type        = bool
    default     = true
}

# ========================== #
#          OUTPUTS           #
# ========================== #

# 🚀 ID do cluster EKS
output "eks_cluster_id" {
    description = "The ID of the EKS cluster"
    value       = module.eks.cluster_id
}

# 🚀 Nome do CloudWatch Log Group (somente se logs estiverem ativados)
output "eks_cloudwatch_log_group" {
    description = "The CloudWatch Log Group for EKS cluster"
    value       = var.enable_logging ? aws_cloudwatch_log_group.eks_logs.name : "Logging disabled"
}

# 🚀 Informações do Banco de Dados (Somente se banco estiver ativado)
output "database_endpoint" {
    description = "The endpoint of the AI service database"
    value       = var.enable_database ? aws_db_instance.ai_service_db.endpoint : "Database disabled"
    sensitive   = true
}

output "database_name" {
    description = "The name of the AI service database"
    value       = var.enable_database ? aws_db_instance.ai_service_db.name : "Database disabled"
}

output "database_port" {
    description = "The port on which the AI service database is listening"
    value       = var.enable_database ? aws_db_instance.ai_service_db.port : "Database disabled"
}

# 🚀 Informações da Rede (Exportação completa)
output "vpc_id" {
    description = "The ID of the VPC"
    value       = aws_vpc.main.id
}

output "public_subnet_ids" {
    description = "List of public subnet IDs"
    value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
    description = "List of private subnet IDs"
    value       = aws_subnet.private[*].id
}
