from collections import Counter
from threading import Lock


class MetricsRegistry:
    """Small dependency-free Prometheus registry for core service signals."""

    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()
        self._latency_ms = 0
        self._lock = Lock()

    def record_score(self, decision: str, latency_ms: int) -> None:
        with self._lock:
            self._counts["requests"] += 1
            self._counts[f"decision_{decision.lower()}"] += 1
            self._latency_ms += latency_ms

    def render(self) -> str:
        with self._lock:
            lines = [
                "# HELP sentinelpay_scoring_requests_total Scoring requests.",
                "# TYPE sentinelpay_scoring_requests_total counter",
                f"sentinelpay_scoring_requests_total {self._counts['requests']}",
            ]
            for decision in ("approve", "review", "decline"):
                lines.extend(
                    [
                        "# TYPE sentinelpay_decisions_total counter",
                        "sentinelpay_decisions_total"
                        f'{{decision="{decision.upper()}"}} '
                        f"{self._counts[f'decision_{decision}']}",
                    ]
                )
            lines.extend(
                [
                    "# TYPE sentinelpay_scoring_latency_ms_total counter",
                    f"sentinelpay_scoring_latency_ms_total {self._latency_ms}",
                ]
            )
            return "\n".join(lines) + "\n"


metrics = MetricsRegistry()
