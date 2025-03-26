import json
import logging
from typing import Dict, Any, Optional, Callable
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from dataclasses import dataclass
from contextlib import contextmanager
import signal
import sys
from datetime import datetime

@dataclass
class KafkaConfig:
    """Configurações do Kafka"""
    bootstrap_servers: str
    topic: str
    group_id: str
    auto_offset_reset: str = 'earliest'
    enable_auto_commit: bool = True

class RealTimeAnalytics:
    """
    Consome eventos de transações em tempo real e fornece insights imediatos.
    Implementa padrões robustos para uso em produção.
    """

    def __init__(self, config: KafkaConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.running = False
        self.consumer = None
        self._setup_signal_handling()

    def _setup_logging(self) -> logging.Logger:
        """Configura o sistema de logging"""
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def _setup_signal_handling(self):
        """Configura o tratamento de sinais para graceful shutdown"""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Manipula sinais de término"""
        self.logger.info("Recebido sinal de término. Iniciando shutdown graceful...")
        self.running = False

    def _create_consumer(self) -> KafkaConsumer:
        """Cria e configura o consumidor Kafka"""
        try:
            return KafkaConsumer(
                self.config.topic,
                bootstrap_servers=self.config.bootstrap_servers,
                group_id=self.config.group_id,
                auto_offset_reset=self.config.auto_offset_reset,
                enable_auto_commit=self.config.enable_auto_commit,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                security_protocol='PLAINTEXT'  # Ajuste conforme necessário
            )
        except KafkaError as e:
            self.logger.error(f"Erro ao criar consumidor Kafka: {e}")
            raise

    @contextmanager
    def connect(self):
        """Gerenciador de contexto para conexão segura"""
        try:
            self.consumer = self._create_consumer()
            self.logger.info("Consumidor Kafka conectado com sucesso")
            yield self
        finally:
            if self.consumer:
                self.consumer.close()
                self.logger.info("Conexão com Kafka fechada")

    def process_message(self, message: Dict[str, Any]) -> None:
        """Processa cada mensagem recebida"""
        try:
            # Adicione sua lógica de processamento aqui
            timestamp = datetime.now().isoformat()
            self.logger.info(f"[{timestamp}] Processando evento: {message}")
            
            # Exemplo de validação básica
            if not isinstance(message, dict):
                raise ValueError("Mensagem inválida: deve ser um dicionário")
            
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {e}")
            # Aqui você pode adicionar lógica para dead letter queue

    def consume_messages(self, batch_timeout_ms: int = 1000):
        """Consome mensagens do Kafka de forma segura e eficiente"""
        self.running = True
        
        try:
            while self.running:
                message_batch = self.consumer.poll(timeout_ms=batch_timeout_ms)
                
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            self.process_message(message.value)
                        except Exception as e:
                            self.logger.error(f"Erro no processamento: {e}")
                            continue
                
                self.consumer.commit()  # Commit explícito após processamento
                
        except Exception as e:
            self.logger.error(f"Erro fatal no consumo de mensagens: {e}")
            raise
        finally:
            self.logger.info("Finalizando consumo de mensagens")

def main():
    config = KafkaConfig(
        bootstrap_servers="localhost:9092",
        topic="realtime_analytics",
        group_id="analytics_group"
    )
    
    analytics = RealTimeAnalytics(config)
    
    with analytics.connect():
        analytics.consume_messages()

if __name__ == "__main__":
    main()
