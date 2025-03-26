import requests
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_alert(message: str):
    if not SLACK_WEBHOOK_URL:
        print("⚠️ Webhook do Slack não configurado")
        return

    payload = {"text": f"🚨 ALERTA: {message}"}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

def alert_high_latency(endpoint: str, latency: float):
    if latency > 1.0:
        send_alert(f"Latência alta detectada em {endpoint}: {latency}s")
        def alert_critical_latency(endpoint: str, latency: float, threshold: float = 5.0):
            if latency > threshold:
                send_alert(f"⚠️ LATÊNCIA CRÍTICA em {endpoint}: {latency}s - Sistema pode estar comprometido!")

        def alert_error_rate(endpoint: str, error_rate: float, threshold: float = 0.1):
            if error_rate > threshold:
                send_alert(f"❌ Taxa de erro elevada em {endpoint}: {error_rate*100:.1f}%")

        def alert_memory_usage(service: str, usage_mb: float, threshold_mb: float = 1000):
            if usage_mb > threshold_mb:
                send_alert(f"📈 Uso de memória elevado em {service}: {usage_mb:.0f}MB")

        def alert_disk_space(path: str, free_space_gb: float, min_free_gb: float = 10):
            if free_space_gb < min_free_gb:
                send_alert(f"💾 Espaço em disco baixo em {path}: {free_space_gb:.1f}GB livres")
