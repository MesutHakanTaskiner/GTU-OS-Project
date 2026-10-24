"""Public dispatcher for all supported scheduling policies."""

from __future__ import annotations

from collections.abc import Sequence

from .fcfs import schedule_fcfs
from .metrics import calculate_metrics
from .models import ProcessSpec, SimulationResult
from .round_robin import schedule_round_robin
from .sjf import schedule_sjf
from .srtf import schedule_srtf
from .validation import ValidationError, validate_processes, validate_quantum

ALGORITHMS = ("FCFS", "SJF", "SRTF", "Round Robin")


def simulate(
    processes: Sequence[ProcessSpec], algorithm: str, quantum: int | None = None
) -> SimulationResult:
    validated = validate_processes(processes)
    normalized = algorithm.strip() if isinstance(algorithm, str) else ""
    if normalized not in ALGORITHMS:
        raise ValidationError(
            f"Unknown algorithm. Choose one of: {', '.join(ALGORITHMS)}."
        )

    actual_quantum: int | None = None
    if normalized == "FCFS":
        segments, trace = schedule_fcfs(validated)
    elif normalized == "SJF":
        segments, trace = schedule_sjf(validated)
    elif normalized == "SRTF":
        segments, trace = schedule_srtf(validated)
    else:
        actual_quantum = validate_quantum(quantum)
        segments, trace = schedule_round_robin(validated, actual_quantum)

    metrics = calculate_metrics(validated, segments)
    count = len(metrics)
    return SimulationResult(
        algorithm=normalized,
        quantum=actual_quantum,
        segments=segments,
        per_process_metrics=metrics,
        average_turnaround=sum(item.turnaround for item in metrics) / count,
        average_waiting=sum(item.waiting for item in metrics) / count,
        average_response=sum(item.response for item in metrics) / count,
        decision_trace=trace,
    )

