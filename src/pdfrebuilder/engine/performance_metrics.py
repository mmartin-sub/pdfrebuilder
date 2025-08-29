"""
Performance Metrics Collection for PDF Engines

This module provides utilities for collecting and reporting performance metrics
for different PDF rendering engines.
"""

import logging
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import psutil

logger = logging.getLogger(__name__)


@dataclass
class RenderingMetrics:
    """Data class for rendering performance metrics."""

    engine_name: str
    engine_version: str
    start_time: float
    end_time: float
    duration: float
    memory_start: float
    memory_end: float
    memory_peak: float
    memory_used: float
    cpu_percent: float
    cpu_time_user: float
    cpu_time_system: float
    page_count: int
    element_count: int
    success: bool
    error_message: str | None = None
    warnings: list[str] | None = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return asdict(self)

    def to_summary(self) -> dict[str, Any]:
        """Get a summary of key metrics."""
        return {
            "engine": self.engine_name,
            "duration_ms": round(self.duration * 1000, 2),
            "memory_mb": round(self.memory_used / (1024 * 1024), 2),
            "cpu_time_ms": round((self.cpu_time_user + self.cpu_time_system) * 1000, 2),
            "pages": self.page_count,
            "elements": self.element_count,
            "success": self.success,
            "warnings_count": len(self.warnings) if self.warnings is not None else 0,
        }


class PerformanceCollector:
    """Collector for performance metrics."""

    def __init__(self):
        """Initialize the performance collector."""
        self.metrics_history: list[RenderingMetrics] = []
        self._current_metrics: RenderingMetrics | None = None

    @contextmanager
    def measure_rendering(self, engine_name: str, engine_version: str = "unknown"):
        """
        Context manager for measuring rendering performance.

        Args:
            engine_name: Name of the rendering engine
            engine_version: Version of the rendering engine

        Yields:
            Dictionary for collecting additional metrics during rendering
        """
        # Initialize metrics
        start_time = time.time()
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_start = memory_info.rss

        # Create metrics object
        metrics = RenderingMetrics(
            engine_name=engine_name,
            engine_version=engine_version,
            start_time=start_time,
            end_time=0,
            duration=0,
            memory_start=memory_start,
            memory_end=0,
            memory_peak=memory_start,
            memory_used=0,
            cpu_percent=0,
            cpu_time_user=0,
            cpu_time_system=0,
            page_count=0,
            element_count=0,
            success=False,
        )

        self._current_metrics = metrics

        # Context for collecting additional metrics
        context: dict[str, Any] = {"page_count": 0, "element_count": 0, "warnings": []}

        try:
            # Monitor memory usage during rendering
            memory_peak = memory_start

            # Basic CPU time monitoring
            cpu_start_time = process.cpu_times()

            yield context

            # Mark as successful if no exception
            metrics.success = True

        except Exception as e:
            metrics.success = False
            metrics.error_message = str(e)
            logger.error(f"Rendering failed: {e}")
            raise

        finally:
            # Collect final metrics
            end_time = time.time()
            memory_info = process.memory_info()
            memory_end = memory_info.rss

            # Update metrics
            metrics.end_time = end_time
            metrics.duration = end_time - start_time
            metrics.memory_end = memory_end
            metrics.memory_used = memory_end - memory_start
            metrics.memory_peak = max(memory_peak, memory_end)
            metrics.page_count = int(context["page_count"])
            metrics.element_count = int(context["element_count"])
            metrics.warnings = list(context["warnings"])

            # Get CPU usage (approximate)
            try:
                metrics.cpu_percent = process.cpu_percent()
                # Calculate CPU time used
                cpu_end_time = process.cpu_times()
                metrics.cpu_time_user = cpu_end_time.user - cpu_start_time.user
                metrics.cpu_time_system = cpu_end_time.system - cpu_start_time.system
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                metrics.cpu_percent = 0
                metrics.cpu_time_user = 0
                metrics.cpu_time_system = 0

            # Store metrics
            self.metrics_history.append(metrics)
            self._current_metrics = None

            logger.info(f"Rendering completed: {metrics.to_summary()}")

    def get_current_metrics(self) -> RenderingMetrics | None:
        """Get the currently active metrics object."""
        return self._current_metrics

    def get_latest_metrics(self) -> RenderingMetrics | None:
        """Get the most recent metrics."""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_metrics_history(self) -> list[RenderingMetrics]:
        """Get all collected metrics."""
        return self.metrics_history.copy()

    def get_engine_stats(self, engine_name: str) -> dict[str, Any]:
        """
        Get statistics for a specific engine.

        Args:
            engine_name: Name of the engine

        Returns:
            Statistics dictionary
        """
        engine_metrics = [m for m in self.metrics_history if m.engine_name == engine_name]

        if not engine_metrics:
            return {"engine": engine_name, "runs": 0}

        successful_runs = [m for m in engine_metrics if m.success]
        failed_runs = [m for m in engine_metrics if not m.success]

        stats = {
            "engine": engine_name,
            "total_runs": len(engine_metrics),
            "successful_runs": len(successful_runs),
            "failed_runs": len(failed_runs),
            "success_rate": (len(successful_runs) / len(engine_metrics) if engine_metrics else 0),
        }

        if successful_runs:
            durations = [m.duration for m in successful_runs]
            memory_usage = [m.memory_used for m in successful_runs]

            stats.update(
                {
                    "avg_duration_ms": round(sum(durations) / len(durations) * 1000, 2),
                    "min_duration_ms": round(min(durations) * 1000, 2),
                    "max_duration_ms": round(max(durations) * 1000, 2),
                    "avg_memory_mb": round(sum(memory_usage) / len(memory_usage) / (1024 * 1024), 2),
                    "min_memory_mb": round(min(memory_usage) / (1024 * 1024), 2),
                    "max_memory_mb": round(max(memory_usage) / (1024 * 1024), 2),
                    "total_pages": sum(m.page_count for m in successful_runs),
                    "total_elements": sum(m.element_count for m in successful_runs),
                }
            )

        return stats

    def compare_engines(self, engine1: str, engine2: str) -> dict[str, Any]:
        """
        Compare performance between two engines.

        Args:
            engine1: Name of the first engine
            engine2: Name of the second engine

        Returns:
            Comparison dictionary
        """
        stats1 = self.get_engine_stats(engine1)
        stats2 = self.get_engine_stats(engine2)

        comparison = {"engine1": stats1, "engine2": stats2, "comparison": {}}

        # Compare key metrics
        if stats1.get("successful_runs", 0) > 0 and stats2.get("successful_runs", 0) > 0:
            comparison["comparison"] = {
                "speed_ratio": stats1.get("avg_duration_ms", 0) / stats2.get("avg_duration_ms", 1),
                "memory_ratio": stats1.get("avg_memory_mb", 0) / stats2.get("avg_memory_mb", 1),
                "reliability_diff": stats1.get("success_rate", 0) - stats2.get("success_rate", 0),
            }

        return comparison

    def generate_report(self, output_path: str | None = None) -> dict[str, Any]:
        """
        Generate a comprehensive performance report.

        Args:
            output_path: Optional path to save the report

        Returns:
            Report dictionary
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_runs": len(self.metrics_history),
            "engines": {},
            "summary": {},
        }

        # Get stats for each engine
        engines = {m.engine_name for m in self.metrics_history}
        for engine in engines:
            engine_stats = self.get_engine_stats(engine)
            report["engines"][engine] = engine_stats

        # Overall summary
        if self.metrics_history:
            successful_runs = [m for m in self.metrics_history if m.success]
            report["summary"] = {
                "total_runs": len(self.metrics_history),
                "successful_runs": len(successful_runs),
                "overall_success_rate": len(successful_runs) / len(self.metrics_history),
                "total_pages_processed": sum(m.page_count for m in successful_runs),
                "total_elements_processed": sum(m.element_count for m in successful_runs),
                "total_processing_time_ms": round(sum(m.duration for m in successful_runs) * 1000, 2),
            }

        # Save report if path provided
        if output_path:
            try:
                import json

                with open(output_path, "w") as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Performance report saved to: {output_path}")
            except Exception as e:
                logger.error(f"Error saving report: {e}")

        return report

    def clear_history(self) -> None:
        """Clear all collected metrics."""
        self.metrics_history.clear()
        logger.info("Performance metrics history cleared")


# Global performance collector instance
_performance_collector: PerformanceCollector | None = None


def get_performance_collector() -> PerformanceCollector:
    """Get the global performance collector instance."""
    global _performance_collector
    if _performance_collector is None:
        _performance_collector = PerformanceCollector()
    return _performance_collector


def measure_engine_performance(engine_name: str, engine_version: str = "unknown"):
    """
    Decorator/context manager for measuring engine performance.

    Args:
        engine_name: Name of the rendering engine
        engine_version: Version of the rendering engine

    Returns:
        Context manager for performance measurement
    """
    collector = get_performance_collector()
    return collector.measure_rendering(engine_name, engine_version)


def get_engine_performance_stats(engine_name: str) -> dict[str, Any]:
    """
    Get performance statistics for an engine.

    Args:
        engine_name: Name of the engine

    Returns:
        Performance statistics
    """
    collector = get_performance_collector()
    return collector.get_engine_stats(engine_name)


def generate_performance_report(output_path: str | None = None) -> dict[str, Any]:
    """
    Generate a performance report.

    Args:
        output_path: Optional path to save the report

    Returns:
        Performance report
    """
    collector = get_performance_collector()
    return collector.generate_report(output_path)
