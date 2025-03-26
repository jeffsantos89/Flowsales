from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import psutil
import logging
from enum import Enum
from abc import ABC, abstractmethod
from monitoring import MetricCollector, MetricValue

logger = logging.getLogger(__name__)

class Channel(Enum):
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    MERCADOLIVRE = "mercadolivre"
    SHOPEE = "shopee"
    AMAZON = "amazon"

@dataclass
class SessionMetrics:
    active_sessions: int
    queue_size: int
    response_time_ms: float
    messages_processed: int

class MetricProvider(ABC):
    @abstractmethod
    def get_session_metrics(self, channel: Channel) -> SessionMetrics:
        pass

class BotCollector(MetricCollector):
    """
    Enhanced metrics collector for multichannel bots with sophisticated monitoring capabilities.
    Supports multiple channels and provides detailed metrics about bot performance.
    """

    def __init__(
        self,
        metric_provider: Optional[MetricProvider] = None,
        channels: Optional[List[Channel]] = None
    ):
        self.channels = channels or list(Channel)
        self.metric_provider = metric_provider
        self._initialize_logging()

    def _initialize_logging(self) -> None:
        """Configure detailed logging for the collector."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _collect_channel_metrics(self, channel: Channel, timestamp: datetime) -> Dict[str, MetricValue]:
        """Collect detailed metrics for a specific channel."""
        try:
            metrics = {}
            session_metrics = self.metric_provider.get_session_metrics(channel) if self.metric_provider else None

            metrics.update({
                f"bot_{channel.value}_active_sessions": MetricValue(
                    value=session_metrics.active_sessions if session_metrics else 0,
                    timestamp=timestamp,
                    labels={"channel": channel.value, "type": "sessions"},
                    unit="sessions"
                ),
                f"bot_{channel.value}_queue_size": MetricValue(
                    value=session_metrics.queue_size if session_metrics else 0,
                    timestamp=timestamp,
                    labels={"channel": channel.value, "type": "queue"},
                    unit="messages"
                ),
                f"bot_{channel.value}_response_time": MetricValue(
                    value=session_metrics.response_time_ms if session_metrics else 0,
                    timestamp=timestamp,
                    labels={"channel": channel.value, "type": "latency"},
                    unit="milliseconds"
                ),
                f"bot_{channel.value}_cpu_usage": MetricValue(
                    value=psutil.cpu_percent(interval=0.1),
                    timestamp=timestamp,
                    labels={"channel": channel.value, "type": "system"},
                    unit="percent"
                ),
                f"bot_{channel.value}_memory_usage": MetricValue(
                    value=psutil.Process().memory_percent(),
                    timestamp=timestamp,
                    labels={"channel": channel.value, "type": "system"},
                    unit="percent"
                )
            })
            return metrics
        except Exception as e:
            logger.error(f"Error collecting metrics for channel {channel.value}: {str(e)}")
            return {}

    def collect(self) -> Dict[str, MetricValue]:
        """
        Collect comprehensive metrics for all channels.
        Returns a dictionary of metric names and their corresponding values.
        """
        try:
            metrics = {}
            timestamp = datetime.utcnow()

            for channel in self.channels:
                channel_metrics = self._collect_channel_metrics(channel, timestamp)
                metrics.update(channel_metrics)

            logger.info(f"Successfully collected metrics for {len(self.channels)} channels")
            return metrics

        except Exception as e:
            logger.exception("Critical error in metrics collection")
            raise RuntimeError(f"Failed to collect metrics: {str(e)}") from e
