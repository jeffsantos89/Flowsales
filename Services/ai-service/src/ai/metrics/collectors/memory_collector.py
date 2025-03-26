from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, List
import logging
import psutil
from pathlib import Path
from monitoring import MetricCollector, MetricValue

logger = logging.getLogger(__name__)

@dataclass
class SystemResources:
    """Data container for system resource metrics"""
    virtual_memory: psutil._pslinux.svmem
    swap_memory: psutil._pslinux.sswap
    disk_usage: psutil._common.sdiskusage

class MemoryCollector(MetricCollector):
    """
    Advanced collector for physical memory, swap, and disk usage metrics.
    Optimized for Prometheus monitoring in self-hosted environments.
    
    Features:
    - Comprehensive system resource monitoring
    - Configurable disk paths
    - Error resilience with fallback mechanisms
    - Detailed metric labeling
    """

    def __init__(self, disk_paths: List[str] = None):
        """
        Initialize the collector with configurable disk paths.
        
        Args:
            disk_paths: List of paths to monitor disk usage. Defaults to root (/)
        """
        self.disk_paths = disk_paths or ['/']
        self._validate_paths()

    def _validate_paths(self) -> None:
        """Validate all configured disk paths exist"""
        for path in self.disk_paths:
            if not Path(path).exists():
                raise ValueError(f"Invalid disk path: {path}")

    def _get_system_resources(self) -> SystemResources:
        """Collect system resource metrics with error handling"""
        try:
            return SystemResources(
                virtual_memory=psutil.virtual_memory(),
                swap_memory=psutil.swap_memory(),
                disk_usage=psutil.disk_usage(self.disk_paths[0])
            )
        except Exception as e:
            logger.error(f"Failed to collect system resources: {str(e)}")
            raise RuntimeError("System resource collection failed") from e

    def _create_metric(
        self,
        value: float,
        timestamp: datetime,
        labels: Optional[Dict[str, str]] = None,
        unit: str = ""
    ) -> MetricValue:
        """Create a metric value with standard formatting"""
        return MetricValue(
            value=value,
            timestamp=timestamp,
            labels=labels or {},
            unit=unit
        )

    def collect(self) -> Dict[str, MetricValue]:
        """
        Collect comprehensive system metrics with proper error handling.
        
        Returns:
            Dictionary of metrics with their corresponding values
        
        Raises:
            RuntimeError: If metric collection fails
        """
        try:
            metrics = {}
            timestamp = datetime.utcnow()
            resources = self._get_system_resources()

            # Memory metrics with detailed labels
            memory_labels = {"type": "physical"}
            metrics.update({
                "memory_total": self._create_metric(
                    resources.virtual_memory.total, timestamp, memory_labels, "bytes"),
                "memory_used": self._create_metric(
                    resources.virtual_memory.used, timestamp, memory_labels, "bytes"),
                "memory_available": self._create_metric(
                    resources.virtual_memory.available, timestamp, memory_labels, "bytes"),
                "memory_percent": self._create_metric(
                    resources.virtual_memory.percent, timestamp, memory_labels, "percent")
            })

            # Swap metrics
            swap_labels = {"type": "swap"}
            metrics.update({
                "swap_used": self._create_metric(
                    resources.swap_memory.used, timestamp, swap_labels, "bytes"),
                "swap_percent": self._create_metric(
                    resources.swap_memory.percent, timestamp, swap_labels, "percent")
            })

            # Disk metrics for each monitored path
            for path in self.disk_paths:
                disk_usage = psutil.disk_usage(path)
                disk_labels = {"path": path}
                metrics.update({
                    f"disk_used_{path}": self._create_metric(
                        disk_usage.used, timestamp, disk_labels, "bytes"),
                    f"disk_percent_{path}": self._create_metric(
                        disk_usage.percent, timestamp, disk_labels, "percent")
                })

            return metrics

        except Exception as e:
            logger.exception("Critical error in metric collection")
            raise RuntimeError(f"Metric collection failed: {str(e)}") from e
