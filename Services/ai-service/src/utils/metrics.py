# src/ai/utils/metrics.py
from typing import Dict, List, Optional, Union, Any
import prometheus_client
import threading
from dataclasses import dataclass
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"

@dataclass
class MetricConfig:
    name: str
    description: str
    labels: Optional[Dict[str, str]] = None
    buckets: Optional[List[float]] = None

class MetricsCollector:
    """
    A thread-safe metrics collector for Prometheus metrics.
    Supports counters, gauges, and histograms with label support.
    """
    
    def __init__(self, namespace: str = "", subsystem: str = ""):
        """
        Initialize the metrics collector.
        
        Args:
            namespace: The metrics namespace
            subsystem: The metrics subsystem
        """
        self._lock = threading.RLock()  # Reentrant lock for nested operations
        self._metrics: Dict[str, Dict[str, Any]] = {
            MetricType.COUNTER.value: {},
            MetricType.GAUGE.value: {},
            MetricType.HISTOGRAM.value: {},
        }
        self._namespace = namespace
        self._subsystem = subsystem

    def _create_metric_name(self, name: str) -> str:
        """Create a fully qualified metric name."""
        parts = [part for part in [self._namespace, self._subsystem, name] if part]
        return "_".join(parts)

    def _validate_labels(self, labels: Optional[Dict[str, str]]) -> None:
        """Validate label names and values."""
        if labels:
            if not all(isinstance(k, str) and isinstance(v, str) for k, v in labels.items()):
                raise ValueError("Labels must be strings")
            if not all(k.isidentifier() for k in labels):
                raise ValueError("Label names must be valid Python identifiers")

    def _get_or_create_metric(
        self,
        metric_type: MetricType,
        config: MetricConfig,
    ) -> Any:
        """Get existing or create new metric."""
        key = self._metric_key(config.name, config.labels)
        
        with self._lock:
            metrics_dict = self._metrics[metric_type.value]
            if key not in metrics_dict:
                metric_name = self._create_metric_name(config.name)
                label_names = list(config.labels.keys()) if config.labels else []
                
                if metric_type == MetricType.COUNTER:
                    metrics_dict[key] = prometheus_client.Counter(
                        metric_name, config.description, labelnames=label_names
                    )
                elif metric_type == MetricType.GAUGE:
                    metrics_dict[key] = prometheus_client.Gauge(
                        metric_name, config.description, labelnames=label_names
                    )
                elif metric_type == MetricType.HISTOGRAM:
                    metrics_dict[key] = prometheus_client.Histogram(
                        metric_name, config.description, labelnames=label_names,
                        buckets=config.buckets or prometheus_client.Histogram.DEFAULT_BUCKETS
                    )
                logger.debug(f"Created new {metric_type.value}: {metric_name}")
            
            return metrics_dict[key]

    def increment(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None,
        value: float = 1.0,
        description: str = ""
    ) -> None:
        """Increment a counter."""
        try:
            self._validate_labels(labels)
            config = MetricConfig(name=name, description=description or f"{name} counter", labels=labels)
            counter = self._get_or_create_metric(MetricType.COUNTER, config)
            
            if labels:
                counter.labels(**labels).inc(value)
            else:
                counter.inc(value)
        except Exception as e:
            logger.error(f"Error incrementing counter {name}: {str(e)}")
            raise

    def gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        description: str = ""
    ) -> None:
        """Set a gauge value."""
        try:
            self._validate_labels(labels)
            config = MetricConfig(name=name, description=description or f"{name} gauge", labels=labels)
            gauge = self._get_or_create_metric(MetricType.GAUGE, config)
            
            if labels:
                gauge.labels(**labels).set(value)
            else:
                gauge.set(value)
        except Exception as e:
            logger.error(f"Error setting gauge {name}: {str(e)}")
            raise

    def observe(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        buckets: Optional[List[float]] = None,
        description: str = ""
    ) -> None:
        """Observe a histogram value."""
        try:
            self._validate_labels(labels)
            config = MetricConfig(
                name=name,
                description=description or f"{name} histogram",
                labels=labels,
                buckets=buckets
            )
            histogram = self._get_or_create_metric(MetricType.HISTOGRAM, config)
            
            if labels:
                histogram.labels(**labels).observe(value)
            else:
                histogram.observe(value)
        except Exception as e:
            logger.error(f"Error observing histogram {name}: {str(e)}")
            raise

    def get_all(self) -> Dict[str, List[str]]:
        """Get all registered metrics."""
        with self._lock:
            return {
                "counters": list(self._metrics[MetricType.COUNTER.value].keys()),
                "gauges": list(self._metrics[MetricType.GAUGE.value].keys()),
                "histograms": list(self._metrics[MetricType.HISTOGRAM.value].keys()),
            }

    def _metric_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Generate a unique key for a metric."""
        if labels:
            return f"{name}_" + "_".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return name

    def clear(self) -> None:
        """Clear all metrics (useful for testing)."""
        with self._lock:
            for metric_dict in self._metrics.values():
                metric_dict.clear()
