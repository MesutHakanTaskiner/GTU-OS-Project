"""First-Come, First-Served scheduling."""

from __future__ import annotations

from .common import append_segment
from .models import ExecutionSegment, ProcessSpec


def schedule_fcfs(processes: tuple[ProcessSpec, ...]) -> tuple[tuple[ExecutionSegment, ...], tuple[str, ...]]:
    segments: list[ExecutionSegment] = []
    trace: list[str] = []
    time = 0
    for process in sorted(processes, key=lambda p: (p.arrival, p.input_index)):
        if time < process.arrival:
            append_segment(segments, None, time, process.arrival, merge_adjacent=True)
            trace.append(f"t={time}: no process is ready; CPU idles until t={process.arrival}.")
            time = process.arrival
        start = time
        time += process.burst
        append_segment(segments, process.pid, start, time, merge_adjacent=True)
        trace.append(
            f"t={start}: {process.pid} is the earliest-arriving ready process and runs to completion at t={time}."
        )
    return tuple(segments), tuple(trace)

