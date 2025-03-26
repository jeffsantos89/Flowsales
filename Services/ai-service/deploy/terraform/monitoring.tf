# ========================== #
#    VARIÁVEIS UTILIZÁVEIS   #
# ========================== #
variable "sns_topic_name" {
    description = "Nome do tópico SNS"
    type        = string
    default     = "ai-service-alerts"
}

variable "sns_email_endpoint" {
    description = "Email para receber notificações"
    type        = string
    default     = "admin@empresa.com"
}

variable "cpu_alarm_threshold" {
    description = "Threshold para alarme de CPU"
    type        = number
    default     = 80
}

variable "memory_alarm_threshold" {
    description = "Threshold para alarme de Memória"
    type        = number
    default     = 75
}

variable "latency_alarm_threshold" {
    description = "Threshold para latência da aplicação"
    type        = number
    default     = 300  # Tempo em milissegundos
}

variable "log_retention_days" {
    description = "Dias de retenção dos logs"
    type        = number
    default     = 30
}

variable "cloudwatch_namespace" {
    description = "Namespace para métricas do CloudWatch"
    type        = string
    default     = "AWS/EKS"
}

variable "eks_log_group" {
    description = "Grupo de logs do EKS"
    type        = string
    default     = "/aws/eks/ai-service"
}

# ========================== #
#    SNS PARA ALERTAS        #
# ========================== #
resource "aws_sns_topic" "sns_topic" {
    name = var.sns_topic_name
}

resource "aws_sns_topic_subscription" "sns_email_subscription" {
    topic_arn = aws_sns_topic.sns_topic.arn
    protocol  = "email"
    endpoint  = var.sns_email_endpoint
}

# ========================== #
#   CLOUDWATCH ALARMES       #
# ========================== #
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
    alarm_name          = "HighCPUUtilization"
    alarm_description   = "Alerta para CPU alta no cluster EKS"
    metric_name         = "CPUUtilization"
    namespace           = var.cloudwatch_namespace
    statistic           = "Average"
    period              = 300
    evaluation_periods  = 2  # Avalia em 2 períodos consecutivos
    threshold           = var.cpu_alarm_threshold
    comparison_operator = "GreaterThanOrEqualToThreshold"
    alarm_actions       = [aws_sns_topic.sns_topic.arn]
    actions_enabled     = true
    treat_missing_data  = "breaching"  # Assume que os dados ausentes são críticos
}

resource "aws_cloudwatch_metric_alarm" "high_memory" {
    alarm_name          = "HighMemoryUsage"
    alarm_description   = "Alerta para uso excessivo de memória"
    metric_name         = "MemoryUtilization"
    namespace           = var.cloudwatch_namespace
    statistic           = "Average"
    period              = 300
    evaluation_periods  = 2
    threshold           = var.memory_alarm_threshold
    comparison_operator = "GreaterThanOrEqualToThreshold"
    alarm_actions       = [aws_sns_topic.sns_topic.arn]
    actions_enabled     = true
    treat_missing_data  = "breaching"
}

resource "aws_cloudwatch_metric_alarm" "high_latency" {
    alarm_name          = "HighLatencyWarning"
    alarm_description   = "Alerta para alta latência na API"
    metric_name         = "RequestLatency"
    namespace           = var.cloudwatch_namespace
    statistic           = "Average"
    period              = 300
    evaluation_periods  = 3
    threshold           = var.latency_alarm_threshold
    comparison_operator = "GreaterThanThreshold"
    alarm_actions       = [aws_sns_topic.sns_topic.arn]
    actions_enabled     = true
    treat_missing_data  = "notBreaching"
}

# ========================== #
#   LOGGING NO CLOUDWATCH    #
# ========================== #
resource "aws_cloudwatch_log_group" "ai_service_logs" {
    name              = var.eks_log_group
    retention_in_days = var.log_retention_days

    tags = {
        Environment = "production"
        Service     = "ai-service"
    }
}

resource "aws_cloudwatch_log_stream" "eks_logs" {
    name           = "ai-service-log-stream"
    log_group_name = aws_cloudwatch_log_group.ai_service_logs.name
}

# ========================== #
#   IAM ROLE PARA LOGGING    #
# ========================== #
resource "aws_iam_role" "eks_logging_role" {
    name = "eks-logging-role"

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
}

resource "aws_iam_role_policy" "eks_logging_policy" {
    name   = "eks-logging-policy"
    role   = aws_iam_role.eks_logging_role.id
    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Action = [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ]
                Resource = "${aws_cloudwatch_log_group.ai_service_logs.arn}:*"
            }
        ]
    })
}

# ========================== #
#          OUTPUTS           #
# ========================== #
output "sns_topic_arn" {
    description = "ARN do SNS para alertas"
    value       = aws_sns_topic.sns_topic.arn
}

output "cloudwatch_log_group_name" {
    description = "Nome do grupo de logs do CloudWatch"
    value       = aws_cloudwatch_log_group.ai_service_logs.name
}

output "eks_logging_role_arn" {
    description = "ARN da role de logging do EKS"
    value       = aws_iam_role.eks_logging_role.arn
}
