"""Metric derivation from a completed execution timeline."""

from __future__ import annotations

from .models import ExecutionSegment, ProcessMetrics, ProcessSpec


def calculate_metrics(
    processes: tuple[ProcessSpec, ...], segments: tuple[ExecutionSegment, ...]
) -> tuple[ProcessMetrics, ...]:
    metrics: list[ProcessMetrics] = []
    for process in sorted(processes, key=lambda p: p.input_index):
        own_segments = [segment for segment in segments if segment.pid == process.pid]
        if not own_segments:
            raise ValueError(f"No execution segment found for {process.pid}.")
        first_start = own_segments[0].start
        completion = own_segments[-1].end
        turnaround = completion - process.arrival
        waiting = turnaround - process.burst
        response = first_start - process.arrival
        metrics.append(
            ProcessMetrics(
                pid=process.pid,
                arrival=process.arrival,
                burst=process.burst,
                first_start=first_start,
                completion=completion,
                turnaround=turnaround,
                waiting=waiting,
                response=response,
            )
        )
    return tuple(metrics)

