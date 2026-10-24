"""Preemptive Shortest Remaining Time First scheduling."""

from __future__ import annotations

from .common import append_segment
from .models import ExecutionSegment, ProcessSpec


def schedule_srtf(processes: tuple[ProcessSpec, ...]) -> tuple[tuple[ExecutionSegment, ...], tuple[str, ...]]:
    remaining = {process.input_index: process.burst for process in processes}
    by_index = {process.input_index: process for process in processes}
    segments: list[ExecutionSegment] = []
    trace: list[str] = []
    current: ProcessSpec | None = None
    time = 0

    while any(value > 0 for value in remaining.values()):
        ready = [
            process
            for process in processes
            if process.arrival <= time and remaining[process.input_index] > 0
        ]
        if not ready:
            next_arrival = min(
                process.arrival
                for process in processes
                if remaining[process.input_index] > 0
            )
            append_segment(segments, None, time, next_arrival, merge_adjacent=True)
            trace.append(f"t={time}: no process is ready; CPU idles until t={next_arrival}.")
            time = next_arrival
            current = None
            continue

        if current is None:
            current = min(
                ready,
                key=lambda p: (remaining[p.input_index], p.arrival, p.input_index),
            )
            trace.append(
                f"t={time}: {current.pid} is selected with remaining time {remaining[current.input_index]}."
            )

        future_arrivals = [
            process.arrival
            for process in processes
            if process.arrival > time and remaining[process.input_index] > 0
        ]
        completion_time = time + remaining[current.input_index]
        next_event = min(completion_time, min(future_arrivals, default=completion_time))
        elapsed = next_event - time
        append_segment(segments, current.pid, time, next_event, merge_adjacent=True)
        remaining[current.input_index] -= elapsed
        time = next_event

        if remaining[current.input_index] == 0:
            trace.append(f"t={time}: {current.pid} completes.")
            current = None
            continue

        contenders = [
            process
            for process in processes
            if process.input_index != current.input_index
            and process.arrival <= time
            and remaining[process.input_index] > 0
            and remaining[process.input_index] < remaining[current.input_index]
        ]
        if contenders:
            replacement = min(
                contenders,
                key=lambda p: (remaining[p.input_index], p.arrival, p.input_index),
            )
            trace.append(
                f"t={time}: {replacement.pid} strictly shorter ({remaining[replacement.input_index]}) than "
                f"{current.pid} ({remaining[current.input_index]}); preemption occurs."
            )
            current = by_index[replacement.input_index]
        else:
            trace.append(
                f"t={time}: no ready process is strictly shorter than {current.pid}; it keeps the CPU."
            )

    return tuple(segments), tuple(trace)

