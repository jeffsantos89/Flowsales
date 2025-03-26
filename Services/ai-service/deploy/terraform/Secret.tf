resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "ai-service-secrets"
    namespace = var.namespace
    labels = {
      app = var.app_name
    }
  }

  data = {
    DATABASE_URL      = base64encode(var.db_credentials)
    REDIS_PASSWORD    = base64encode(var.redis_password)
    ADDITIONAL_SECRET = base64encode(var.additional_secret)
  }

  type = "Opaque"
}
resource "kubernetes_secret" "app_tls_secrets" {
    metadata {
        name      = "ai-service-tls-secrets"
        namespace = var.namespace
        labels = {
            app     = var.app_name
            purpose = "tls"
        }
        annotations = {
            "kubernetes.io/created-by" = "terraform"
            "rotation-date"           = timestamp()
        }
    }

    data = {
        "tls.crt" = base64encode(var.tls_certificate)
        "tls.key" = base64encode(var.tls_private_key)
    }

    type = "kubernetes.io/tls"

    lifecycle {
        prevent_destroy = true
        ignore_changes  = [metadata[0].annotations]
    }
}