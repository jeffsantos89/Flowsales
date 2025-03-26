from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MetricValue:
    """Data class to store metric values with metadata"""
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    unit: str

class MetricCollector(ABC):
    """Abstract base class for metric collection"""
    @abstractmethod
    def collect(self) -> Dict[str, MetricValue]:
        """Collect metrics and return as dictionary"""
        pass

class MetricsRegistry:
    """Central registry for managing metrics"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize metrics registry"""
        self._metrics: Dict[str, MetricValue] = {}
        self._collectors: Dict[str, MetricCollector] = {}
        self._last_update: Optional[datetime] = None
        logger.info("Metrics registry initialized")

    def register_collector(self, name: str, collector: MetricCollector) -> None:
        """Register a new metric collector"""
        try:
            if name in self._collectors:
                raise ValueError(f"Collector {name} already registered")
            self._collectors[name] = collector
            logger.info(f"Registered collector: {name}")
        except Exception as e:
            logger.error(f"Error registering collector {name}: {str(e)}")
            raise

    def update_metric(self, name: str, value: float, labels: Dict[str, str] = None, unit: str = "") -> None:
        """Update a metric value"""
        try:
            self._metrics[name] = MetricValue(
                value=value,
                timestamp=datetime.utcnow(),
                labels=labels or {},
                unit=unit
            )
        except Exception as e:
            logger.error(f"Error updating metric {name}: {str(e)}")
            raise

    def get_metric(self, name: str) -> Optional[MetricValue]:
        """Get a metric value"""
        return self._metrics.get(name)

    def get_all_metrics(self) -> Dict[str, MetricValue]:
        """Get all metrics"""
        return self._metrics.copy()

    def collect_all(self) -> Dict[str, Any]:
        """Collect all metrics from registered collectors"""
        try:
            for collector in self._collectors.values():
                metrics = collector.collect()
                self._metrics.update(metrics)
            self._last_update = datetime.utcnow()
            return self.get_all_metrics()
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            raise

# Create global registry instance
metrics_registry = MetricsRegistry()

__all__ = [
    'MetricValue',
    'MetricCollector',
    'MetricsRegistry',
    'metrics_registry'
]