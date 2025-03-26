resource "kubernetes_stateful_set" "redis_cluster" {
    metadata {
        name      = "redis-cluster"
        namespace = "cache"
        labels = {
            app       = "redis-cluster"
            component = "cache"
            tier      = "backend"
        }
    }

    spec {
        service_name = "redis-cluster"
        replicas     = 6  # Aumentado para melhor alta disponibilidade
        update_strategy {
            type = "RollingUpdate"
            rolling_update {
                partition = 0
            }
        }
        pod_management_policy = "OrderedReady"

        selector {
            match_labels = {
                app = "redis-cluster"
            }
        }

        template {
            metadata {
                labels = {
                    app       = "redis-cluster"
                    component = "cache"
                    tier      = "backend"
                }
                annotations = {
                    "prometheus.io/scrape" = "true"
                    "prometheus.io/port"   = "9121"
                }
            }

            spec {
                termination_grace_period_seconds = 30
                security_context {
                    fs_group = 1000
                    run_as_non_root = true
                    run_as_user     = 1000
                }

                init_container {
                    name  = "init-redis"
                    image = "busybox:1.28"
                    command = ["sh", "-c", "echo never > /sys/kernel/mm/transparent_hugepage/enabled"]
                    security_context {
                        privileged = true
                    }
                }

                container {
                    name  = "redis"
                    image = "redis:7.0-alpine"  # Versão mais recente e imagem alpine para maior segurança

                    command = ["redis-server"]
                    args    = ["--requirepass ${var.redis_password}", "--maxmemory-policy allkeys-lru", "--maxmemory 1536mb"]

                    port {
                        name           = "redis"
                        container_port = 6379
                    }

                    env {
                        name  = "REDIS_PASSWORD"
                        value_from {
                            secret_key_ref {
                                name = "redis-secret"
                                key  = "password"
                            }
                        }
                    }

                    volume_mount {
                        name       = "redis-storage"
                        mount_path = "/data"
                    }

                    resources {
                        limits = {
                            cpu    = "2"
                            memory = "3Gi"
                        }
                        requests = {
                            cpu    = "1"
                            memory = "2Gi"
                        }
                    }

                    liveness_probe {
                        exec {
                            command = ["redis-cli", "ping"]
                        }
                        initial_delay_seconds = 30
                        period_seconds        = 10
                        timeout_seconds      = 5
                        failure_threshold    = 3
                    }

                    readiness_probe {
                        exec {
                            command = ["redis-cli", "ping"]
                        }
                        initial_delay_seconds = 5
                        period_seconds        = 10
                        timeout_seconds      = 5
                        failure_threshold    = 3
                    }

                    startup_probe {
                        exec {
                            command = ["redis-cli", "ping"]
                        }
                        failure_threshold = 30
                        period_seconds    = 10
                    }

                    lifecycle {
                        pre_stop {
                            exec {
                                command = ["/bin/sh", "-c", "redis-cli SHUTDOWN"]
                            }
                        }
                    }
                }

                container {
                    name  = "redis-exporter"
                    image = "oliver006/redis_exporter:v1.44.0"
                    
                    port {
                        container_port = 9121
                        name          = "metrics"
                    }

                    resources {
                        limits = {
                            cpu    = "200m"
                            memory = "256Mi"
                        }
                        requests = {
                            cpu    = "100m"
                            memory = "128Mi"
                        }
                    }
                }

                volume {
                    name = "redis-storage"
                    persistent_volume_claim {
                        claim_name = "redis-pvc"
                    }
                }
            }
        }

        volume_claim_template {
            metadata {
                name = "redis-pvc"
            }

            spec {
                access_modes = ["ReadWriteOnce"]
                storage_class_name = "standard"  # Ajuste conforme sua necessidade

                resources {
                    requests = {
                        storage = "20Gi"  # Aumentado para mais capacidade
                    }
                }
            }
        }
    }
}
