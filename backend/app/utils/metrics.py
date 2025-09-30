"""
Application metrics and performance monitoring utilities.
"""
import time
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and stores application metrics."""

    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self.request_times = deque(maxlen=max_entries)
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'avg_time': 0,
            'max_time': 0,
            'min_time': float('inf')
        })
        self.error_counts = defaultdict(int)
        self.status_codes = defaultdict(int)
        self.start_time = time.time()

    def record_request(self, method: str, path: str, status_code: int,
                      response_time: float, error: Optional[str] = None):
        """Record a request metric."""
        timestamp = datetime.utcnow()

        # Store request time
        self.request_times.append({
            'timestamp': timestamp,
            'method': method,
            'path': path,
            'status_code': status_code,
            'response_time': response_time,
            'error': error
        })

        # Update endpoint statistics
        endpoint_key = f"{method} {path}"
        stats = self.endpoint_stats[endpoint_key]
        stats['count'] += 1
        stats['total_time'] += response_time
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['max_time'] = max(stats['max_time'], response_time)
        stats['min_time'] = min(stats['min_time'], response_time)

        # Update status code counts
        self.status_codes[status_code] += 1

        # Record errors
        if error:
            self.error_counts[error] += 1

    def get_metrics_summary(self) -> Dict:
        """Get a summary of collected metrics."""
        now = time.time()
        uptime = now - self.start_time

        # Calculate recent metrics (last 5 minutes)
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        recent_requests = [
            req for req in self.request_times
            if req['timestamp'] > five_minutes_ago
        ]

        return {
            'uptime_seconds': uptime,
            'total_requests': len(self.request_times),
            'recent_requests_5min': len(recent_requests),
            'avg_response_time': (
                sum(req['response_time'] for req in recent_requests) / len(recent_requests)
                if recent_requests else 0
            ),
            'requests_per_minute': len(recent_requests) / 5 if recent_requests else 0,
            'endpoint_stats': dict(self.endpoint_stats),
            'status_codes': dict(self.status_codes),
            'error_counts': dict(self.error_counts),
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_endpoint_performance(self, limit: int = 10) -> List[Dict]:
        """Get top performing/problematic endpoints."""
        endpoints = []
        for endpoint, stats in self.endpoint_stats.items():
            endpoints.append({
                'endpoint': endpoint,
                'count': stats['count'],
                'avg_response_time': stats['avg_time'],
                'max_response_time': stats['max_time'],
                'min_response_time': stats['min_time'] if stats['min_time'] != float('inf') else 0
            })

        # Sort by average response time (slowest first)
        return sorted(endpoints, key=lambda x: x['avg_response_time'], reverse=True)[:limit]


# Global metrics collector instance
metrics_collector = MetricsCollector()


class PerformanceMonitor:
    """Context manager for monitoring function performance."""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time

        if duration > 1.0:  # Log slow operations
            logger.warning(f"Slow operation: {self.operation_name} took {duration:.4f}s")
        else:
            logger.debug(f"Operation: {self.operation_name} took {duration:.4f}s")


def monitor_performance(operation_name: str):
    """Decorator for monitoring function performance."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            with PerformanceMonitor(operation_name):
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            with PerformanceMonitor(operation_name):
                return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator