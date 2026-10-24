"""Non-preemptive Shortest Job First scheduling."""

from __future__ import annotations

from .common import append_segment
from .models import ExecutionSegment, ProcessSpec


def schedule_sjf(processes: tuple[ProcessSpec, ...]) -> tuple[tuple[ExecutionSegment, ...], tuple[str, ...]]:
    pending = list(processes)
    segments: list[ExecutionSegment] = []
    trace: list[str] = []
    time = 0

    while pending:
        ready = [process for process in pending if process.arrival <= time]
        if not ready:
            next_arrival = min(process.arrival for process in pending)
            append_segment(segments, None, time, next_arrival, merge_adjacent=True)
            trace.append(f"t={time}: no process is ready; CPU idles until t={next_arrival}.")
            time = next_arrival
            continue
        process = min(ready, key=lambda p: (p.burst, p.arrival, p.input_index))
        pending.remove(process)
        start = time
        time += process.burst
        append_segment(segments, process.pid, start, time, merge_adjacent=True)
        trace.append(
            f"t={start}: {process.pid} has the shortest original burst among ready processes and runs non-preemptively to t={time}."
        )
    return tuple(segments), tuple(trace)

