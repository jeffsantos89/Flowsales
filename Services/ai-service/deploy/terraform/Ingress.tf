resource "kubernetes_ingress_v1" "ai_ingress" {
  metadata {
    name      = "ai-service-ingress"
    namespace = var.namespace
    annotations = {
      # SSL/TLS Configuration
      "cert-manager.io/cluster-issuer"                       = "letsencrypt-prod"
      "nginx.ingress.kubernetes.io/ssl-redirect"             = "true"
      "nginx.ingress.kubernetes.io/force-ssl-redirect"       = "true"
      "nginx.ingress.kubernetes.io/ssl-protocols"            = "TLSv1.2 TLSv1.3"
      
      # Security Headers
      "nginx.ingress.kubernetes.io/security-headers"         = "true"
      "nginx.ingress.kubernetes.io/x-frame-options"          = "DENY"
      "nginx.ingress.kubernetes.io/x-content-type-options"   = "nosniff"
      "nginx.ingress.kubernetes.io/hsts"                     = "true"
      "nginx.ingress.kubernetes.io/hsts-max-age"            = "31536000"
      
      # Rate Limiting
      "nginx.ingress.kubernetes.io/limit-rps"               = "10"
      "nginx.ingress.kubernetes.io/limit-connections"       = "5"
      
      # Load Balancing and Backend Configuration
      "nginx.ingress.kubernetes.io/proxy-body-size"          = "10m"
      "nginx.ingress.kubernetes.io/proxy-read-timeout"       = "60"
      "nginx.ingress.kubernetes.io/proxy-send-timeout"       = "60"
      "nginx.ingress.kubernetes.io/proxy-connect-timeout"    = "60"
      "nginx.ingress.kubernetes.io/proxy-buffers-number"     = "4"
      "nginx.ingress.kubernetes.io/proxy-buffer-size"        = "8k"
      
      # CORS Configuration
      "nginx.ingress.kubernetes.io/enable-cors"              = "true"
      "nginx.ingress.kubernetes.io/cors-allow-methods"       = "GET, POST, OPTIONS"
      "nginx.ingress.kubernetes.io/cors-allow-credentials"   = "true"
      "nginx.ingress.kubernetes.io/cors-allow-headers"       = "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization"
      
      # Health Checks
      "nginx.ingress.kubernetes.io/healthcheck-path"         = "/health"
      "nginx.ingress.kubernetes.io/healthcheck-interval"     = "10"
      
      # Load Balancing Algorithm
      "nginx.ingress.kubernetes.io/load-balance"            = "least_conn"
    }
  }

    spec {
        ingress_class_name = "nginx"

        tls {
            secret_name = "ai-service-tls"
            hosts       = [var.netshopmarkt.com]
        }

        rule {
            host = var.netshopmarkt.com

            http {
                path {
                    path      = "/"
                    path_type = "Prefix"

                    backend {
                        service {
                            name = kubernetes_service.ai_service.metadata[0].name
                            port {
                                number = var.service_port
                            }
                        }
                    }
                }

                # Additional path for health checks
                path {
                    path      = "/health"
                    path_type = "Exact"

                    backend {
                        service {
                            name = kubernetes_service.ai_service.metadata[0].name
                            port {
                                number = var.service_port
                            }
                        }
                    }
                }
            }
        }
    }

    lifecycle {
        create_before_destroy = true
    }
}
