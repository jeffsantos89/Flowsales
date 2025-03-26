# ============================= #
#   VARIÁVEIS DE SEGURANÇA      #
# ============================= #

variable "vpc_id" {
  description = "ID do VPC"
  type        = string
}

variable "environment" {
  description = "Ambiente de implantação"
  type        = string
  default     = "Production"
}

variable "ingress_ports" {
  description = "Portas de entrada permitidas"
  type        = list(number)
  default     = [443]
}

variable "ingress_cidr_blocks" {
  description = "Blocos CIDR permitidos para entrada"
  type        = list(string)
  default     = ["192.168.1.0/24", "10.0.0.0/16"]
}

variable "egress_cidr_blocks" {
  description = "Blocos CIDR permitidos para saída"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "tags" {
  description = "Tags para os recursos"
  type        = map(string)
  default     = {
    Environment = "Production"
    Project     = "AI-Service"
  }
}

# ============================= #
#   SECURITY GROUP PARA EKS      #
# ============================= #

resource "aws_security_group" "ai_service_sg" {
  name        = "ai-service-sg"
  description = "Security Group para AI-SERVICE"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_ports
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = var.ingress_cidr_blocks
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.egress_cidr_blocks
  }

  tags = var.tags
}

# ============================= #
#     AWS WAFv2 (PROTEÇÃO)      #
# ============================= #

resource "aws_wafv2_web_acl" "ai_service_wafv2" {
  name        = "ai-service-wafv2"
  description = "Proteção WAFv2 para o AI Service"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name               = "AIServiceWAFMetrics"
    sampled_requests_enabled  = true
  }

  rule {
    name     = "LimitRequests"
    priority = 1
    action {
      count {}
    }
    statement {
      rate_based_statement {
        limit             = 1000
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "LimitRequestsMetric"
      sampled_requests_enabled   = true
    }
  }

  # Proteção contra SQL Injection
  rule {
    name     = "SQLInjectionProtection"
    priority = 2
    action {
      block {}
    }
    statement {
      sqli_match_statement {
        field_to_match {
          uri_path {}
        }
        text_transformation {
          priority = 1
          type     = "URL_DECODE"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "SQLiProtection"
      sampled_requests_enabled   = true
    }
  }

  # Bloqueio de Bots Maliciosos
  rule {
    name     = "BlockBots"
    priority = 3
    action {
      block {}
    }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesBotControlRuleSet"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "BlockBots"
      sampled_requests_enabled   = true
    }
  }

  tags = var.tags
}

# ============================= #
#    AWS GUARD DUTY - ALERTAS   #
# ============================= #

resource "aws_sns_topic" "guardduty_alerts" {
  name = "ai-service-guardduty-alerts"
  tags = var.tags
}

resource "aws_guardduty_detector" "ai_service_guardduty" {
  enable                       = true
  finding_publishing_frequency = "FIFTEEN_MINUTES"
  tags                         = var.tags
}

resource "aws_kms_key" "guardduty_key" {
  description = "KMS key for GuardDuty findings"
  tags        = var.tags
}

resource "aws_guardduty_publishing_destination" "guardduty_logs" {
  detector_id     = aws_guardduty_detector.ai_service_guardduty.id
  destination_arn = aws_sns_topic.guardduty_alerts.arn
  kms_key_arn    = aws_kms_key.guardduty_key.arn
}

# ============================= #
#      SNS PARA ALERTAS         #
# ============================= #

resource "aws_sns_topic_subscription" "guardduty_email_alerts" {
  topic_arn = aws_sns_topic.guardduty_alerts.arn
  protocol  = "email"
  endpoint  = "security-team@empresa.com"
}

resource "aws_sns_topic_subscription" "guardduty_slack_alerts" {
  topic_arn = aws_sns_topic.guardduty_alerts.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.guardduty_to_slack.arn
}

# ============================= #
#      LAMBDA PARA ALERTAS      #
# ============================= #

resource "aws_lambda_function" "guardduty_to_slack" {
  function_name = "GuardDutyToSlack"
  runtime       = "python3.9"
  handler       = "index.lambda_handler"

  role = aws_iam_role.lambda_exec.arn

  filename = "lambda/guardduty_slack.zip"

  environment {
    variables = {
      SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/xxx/yyy/zzz"
    }
  }

  tags = var.tags
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_exec_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
