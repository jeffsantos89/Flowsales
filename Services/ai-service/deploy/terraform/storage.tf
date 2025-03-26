# ================================= #
# 📌 VARIÁVEIS DE CONFIGURAÇÃO
# ================================= #

variable "region" {}
variable "environment" {}
variable "ebs_volume_size" { default = 100 }
variable "ebs_volume_type" { default = "gp3" }
variable "s3_replication_role_arn" {}
variable "backup_bucket_arn" {}

# ================================= #
# 📌 BUCKET S3 PARA LOGS & MODELOS
# ================================= #

resource "aws_s3_bucket" "ai_service_storage" {
  bucket = "ai-service-storage-${var.region}-${var.environment}"
}

resource "aws_s3_bucket_versioning" "ai_service_storage_versioning" {
  bucket = aws_s3_bucket.ai_service_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ai_service_storage_encryption" {
  bucket = aws_s3_bucket.ai_service_storage.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = "alias/aws/s3"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "ai_service_storage_lifecycle" {
  bucket = aws_s3_bucket.ai_service_storage.id

  rule {
    id     = "log-retention"
    status = "Enabled"

    expiration {
      days = 365
    }
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

resource "aws_s3_bucket_logging" "ai_service_storage_logging" {
  bucket = aws_s3_bucket.ai_service_storage.id
  target_bucket = aws_s3_bucket.ai_service_logs.id
  target_prefix = "log/"
}

resource "aws_s3_bucket_acl" "ai_service_storage_acl" {
  bucket = aws_s3_bucket.ai_service_storage.id
  acl    = "private"
}

# 📌 🔒 POLÍTICA MAIS SEGURA PARA S3
resource "aws_s3_bucket_policy" "ai_service_storage_policy" {
  bucket = aws_s3_bucket.ai_service_storage.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::123456789012:role/ai-service-role"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.ai_service_storage.arn}/*"
      },
      {
        Effect = "Deny"
        Principal = "*"
        Action = "s3:PutObject"
        Resource = "${aws_s3_bucket.ai_service_storage.arn}/*"
        Condition = {
          StringNotEqualsIfExists = {
            "aws:PrincipalArn" = "arn:aws:iam::123456789012:role/ai-service-role"
          }
        }
      }
    ]
  })
}

# ================================= #
# 📌 REPLICAÇÃO S3 CROSS-REGION
# ================================= #

resource "aws_s3_bucket_replication_configuration" "ai_service_replication" {
  depends_on = [aws_iam_role_policy_attachment.s3_replication_policy]
  role       = var.s3_replication_role_arn
  bucket     = aws_s3_bucket.ai_service_storage.id

  rule {
    id     = "replication-rule"
    status = "Enabled"

    destination {
      bucket        = var.backup_bucket_arn
      storage_class = "STANDARD_IA"
    }
  }
}

# ================================= #
# 📌 VOLUME EBS PARA PERSISTÊNCIA
# ================================= #

resource "aws_ebs_volume" "ai_service_db" {
  availability_zone = "${var.region}a"
  size             = var.ebs_volume_size
  type             = var.ebs_volume_type
  encrypted        = true
  kms_key_id       = "alias/aws/ebs"

  tags = {
    Name        = "AI Service EBS Volume"
    Environment = var.environment
  }
}

# 📌 📌 SNAPSHOT AUTOMÁTICO DO EBS
resource "aws_ebs_snapshot" "ai_service_snapshot" {
  volume_id = aws_ebs_volume.ai_service_db.id

  tags = {
    Name = "AI Service Snapshot"
  }
}

# 📌 ASSOCIAÇÃO DO EBS COM A EC2 DO BANCO
resource "aws_volume_attachment" "ai_service_db_attachment" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.ai_service_db.id
  instance_id = aws_instance.ai_service_db.id
}

# ================================= #
# 📌 S3 PARA LOGS DO SISTEMA
# ================================= #

resource "aws_s3_bucket" "ai_service_logs" {
  bucket = "ai-service-logs-${var.region}-${var.environment}"

  tags = {
    Name        = "AI Service Logs"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ai_service_logs_encryption" {
  bucket = aws_s3_bucket.ai_service_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_acl" "ai_service_logs_acl" {
  bucket = aws_s3_bucket.ai_service_logs.id
  acl    = "private"
}

resource "aws_s3_bucket_logging" "ai_service_logs_logging" {
  bucket        = aws_s3_bucket.ai_service_logs.id
  target_bucket = aws_s3_bucket.ai_service_logs.bucket
  target_prefix = "log/"
}

# ================================= #
# 📌 IAM ROLE PARA REPLICAÇÃO S3
# ================================= #

resource "aws_iam_role" "s3_replication_role" {
  name = "s3-replication-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "s3_replication_policy" {
  name   = "s3-replication-policy"
  role   = aws_iam_role.s3_replication_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl",
          "s3:GetObjectVersionTagging",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.ai_service_storage.arn}",
          "${aws_s3_bucket.ai_service_storage.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete",
          "s3:ReplicateTags"
        ]
        Resource = "${var.backup_bucket_arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_replication_policy_attachment" {
  role       = aws_iam_role.s3_replication_role.name
  policy_arn = aws_iam_role_policy.s3_replication_policy.arn
}
