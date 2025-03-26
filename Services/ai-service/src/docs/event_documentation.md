# Documentação do Sistema de Eventos - Apache Kafka

## Visão Geral
O AI Service implementa uma arquitetura event-driven robusta para processamento distribuído de previsões e integrações com múltiplos marketplaces, garantindo alta disponibilidade e escalabilidade.

## Tópicos Kafka

### Previsões IA (`ai_predictions`)
- **Propósito**: Processamento assíncrono de previsões dos modelos de IA
- **Partições**: 6
- **Fator de Replicação**: 3
- **Retenção**: 7 dias

### Mensagens WhatsApp (`whatsapp_messages`)
- **Propósito**: Gerenciamento de comunicações via WhatsApp
- **Partições**: 12
- **Fator de Replicação**: 3
- **Retenção**: 30 dias

### Previsões de Vendas (`sales_forecast`)
- **Propósito**: Distribuição de previsões para marketplaces
- **Partições**: 6
- **Fator de Replicação**: 3
- **Retenção**: 14 dias

## Exemplo de Evento (Schema v1.0)
```json
{
    "metadata": {
        "eventId": "evt_123e4567-e89b-12d3-a456-426614174000",
        "type": "prediction_made",
        "version": "1.0",
        "timestamp": "2025-03-18T12:00:00.000Z",
        "producer": "ai-prediction-service"
    },
    "payload": {
        "userId": "usr_1234",
        "marketplaceId": "mkt_789",
        "prediction": {
            "productId": "prd_456",
            "demandLevel": "HIGH",
            "confidence": 0.95,
            "factors": ["seasonality", "market_trends"]
        }
    }
}
```

## Garantias de Entrega
- At-least-once delivery
- Ordenação por chave de partição
- ACKs configurados para `all`

## Monitoramento
- Prometheus metrics
- Grafana dashboards
- Alerting via PagerDuty
