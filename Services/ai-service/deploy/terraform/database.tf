resource "aws_db_instance" "ai_service_db" {
    engine                     = "postgres"
    engine_version             = var.db_engine_version
    instance_class             = var.db_instance_class
    allocated_storage          = var.db_allocated_storage
    max_allocated_storage      = var.db_max_storage
    storage_type               = "gp3"
    username                   = var.db_user
    password                   = var.db_password
    db_name                    = var.db_name
    parameter_group_name       = "default.postgres12"

    backup_retention_period    = var.db_backup_retention
    backup_window              = "03:00-04:00"
    maintenance_window         = "Mon:04:00-Mon:05:00"
    multi_az                   = true
    storage_encrypted          = true
    publicly_accessible        = false
    vpc_security_group_ids     = [aws_security_group.db_sg.id]
    db_subnet_group_name       = aws_db_subnet_group.main.name

    monitoring_interval        = 60
    monitoring_role_arn        = var.monitoring_role_arn

    performance_insights_enabled           = true
    performance_insights_retention_period  = var.performance_insights_retention
    performance_insights_kms_key_id        = var.kms_key_id

    skip_final_snapshot        = !var.enable_final_snapshot
    final_snapshot_identifier  = var.enable_final_snapshot ? "${var.db_name}-final-snapshot" : null
    deletion_protection        = var.enable_deletion_protection

    tags = {
        Name        = "ai-service-db"
        Environment = var.environment
        Managed     = "Terraform"
    }
}

# Security Group para o Banco de Dados
resource "aws_security_group" "db_sg" {
    name        = "db_sg"
    description = "Security Group for AI-Service Database"
    vpc_id      = var.vpc_id

    ingress {
        from_port   = 5432
        to_port     = 5432
        protocol    = "tcp"
        cidr_blocks = var.allowed_cidr_blocks
        description = "Allowed access to database"
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = var.vpc_cidr_blocks
    }

    tags = {
        Name        = "db_sg"
        Environment = var.environment
    }
}

# Subnet Group para o Banco de Dados
resource "aws_db_subnet_group" "main" {
    name       = "ai-service-db-subnet-group"
    subnet_ids = var.db_subnet_ids

    tags = {
        Name        = "ai-service-db-subnet-group"
        Environment = var.environment
    }
}

# Variáveis de Configuração
variable "db_user" {
    description = "Username for the PostgreSQL Database"
    type        = string
}

variable "db_password" {
    description = "Password for the PostgreSQL Database"
    type        = string
    sensitive   = true
}

variable "db_name" {
    description = "Name of the Database"
    type        = string
}

variable "db_engine_version" {
    description = "PostgreSQL Engine Version"
    type        = string
    default     = "12.7"
}

variable "db_instance_class" {
    description = "Instance class for the database"
    type        = string
    default     = "db.t3.medium"
}

variable "db_allocated_storage" {
    description = "Allocated storage in GB"
    type        = number
    default     = 50
}

variable "db_max_storage" {
    description = "Maximum allocated storage in GB"
    type        = number
    default     = 200
}

variable "db_backup_retention" {
    description = "Backup retention period in days"
    type        = number
    default     = 14
}

variable "enable_final_snapshot" {
    description = "Enable final snapshot before deletion"
    type        = bool
    default     = true
}

variable "enable_deletion_protection" {
    description = "Enable deletion protection for the database"
    type        = bool
    default     = true
}

variable "environment" {
    description = "The environment for deployment"
    type        = string
}

variable "vpc_id" {
    description = "The VPC ID for the database"
    type        = string
}

variable "allowed_cidr_blocks" {
    description = "Allowed CIDR blocks for database access"
    type        = list(string)
}

variable "vpc_cidr_blocks" {
    description = "CIDR blocks for the VPC"
    type        = list(string)
}

variable "db_subnet_ids" {
    description = "Subnet IDs for the database"
    type        = list(string)
}

variable "monitoring_role_arn" {
    description = "ARN of the IAM role for enhanced monitoring"
    type        = string
}

variable "kms_key_id" {
    description = "KMS Key ID for encrypting performance insights"
    type        = string
}

variable "performance_insights_retention" {
    description = "Retention period for performance insights (in days)"
    type        = number
    default     = 7
}
