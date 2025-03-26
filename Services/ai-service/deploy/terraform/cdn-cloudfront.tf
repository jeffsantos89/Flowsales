variable "environment" {
  description = "The environment for the deployment"
  type        = string
  default     = "Production"
}

variable "service_name" {
  description = "The name of the service"
  type        = string
  default     = "AI-Service"
}

variable "allowed_geo_locations" {
  description = "List of allowed geo locations"
  type        = list(string)
  default     = ["US", "BR", "DE"]
}

variable "log_bucket" {
  description = "S3 bucket for CloudFront logs"
  type        = string
  default     = "meu-bucket-de-logs.s3.amazonaws.com"
}

variable "log_prefix" {
  description = "Prefix for CloudFront logs"
  type        = string
  default     = "cloudfront-logs/"
}

# Buscando bucket existente (caso não tenha sido criado no Terraform)
data "aws_s3_bucket" "ai_service_static" {
  bucket = "meu-bucket-static"
}

resource "aws_cloudfront_distribution" "cdn" {
  origin {
    domain_name = data.aws_s3_bucket.ai_service_static.website_endpoint
    origin_id   = "AIServiceCDN"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2", "TLSv1.3"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100"
  http_version        = "http2"

  default_cache_behavior {
    target_origin_id       = "AIServiceCDN"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    origin_request_policy_id = "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf" # Managed-CORS-S3Origin

    forwarded_values {
      query_string = false
      headers      = ["Origin"]

      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = var.allowed_geo_locations
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.acm_certificate_arn != "" ? var.acm_certificate_arn : null
    cloudfront_default_certificate = var.acm_certificate_arn == "" ? true : false
    minimum_protocol_version = "TLSv1.2_2021"
  }

  logging_config {
    include_cookies = false
    bucket          = var.log_bucket
    prefix          = var.log_prefix
  }

  tags = {
    Environment = var.environment
    Service     = var.service_name
    Managed     = "Terraform"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  wait_for_deployment = true
}

# Variável opcional para usar um certificado do ACM
variable "acm_certificate_arn" {
  description = "ARN of the ACM certificate for HTTPS"
  type        = string
  default     = ""
}
