"""Round Robin scheduling with explicit quantum-slice boundaries."""

from __future__ import annotations

from collections import deque

from .common import append_segment
from .models import ExecutionSegment, ProcessSpec


def schedule_round_robin(
    processes: tuple[ProcessSpec, ...], quantum: int
) -> tuple[tuple[ExecutionSegment, ...], tuple[str, ...]]:
    arrivals = sorted(processes, key=lambda p: (p.arrival, p.input_index))
    remaining = {process.input_index: process.burst for process in processes}
    queue: deque[ProcessSpec] = deque()
    segments: list[ExecutionSegment] = []
    trace: list[str] = []
    next_arrival_index = 0
    time = 0
    slice_index = 0

    def enqueue_arrivals(up_to_time: int) -> None:
        nonlocal next_arrival_index
        while (
            next_arrival_index < len(arrivals)
            and arrivals[next_arrival_index].arrival <= up_to_time
        ):
            process = arrivals[next_arrival_index]
            queue.append(process)
            trace.append(f"t={process.arrival}: {process.pid} enters the ready queue.")
            next_arrival_index += 1

    while next_arrival_index < len(arrivals) or queue:
        enqueue_arrivals(time)
        if not queue:
            next_time = arrivals[next_arrival_index].arrival
            append_segment(segments, None, time, next_time, merge_adjacent=True)
            trace.append(f"t={time}: ready queue is empty; CPU idles until t={next_time}.")
            time = next_time
            enqueue_arrivals(time)

        process = queue.popleft()
        start = time
        duration = min(quantum, remaining[process.input_index])
        time += duration
        slice_index += 1
        append_segment(
            segments,
            process.pid,
            start,
            time,
            merge_adjacent=False,
            slice_index=slice_index,
        )
        remaining[process.input_index] -= duration
        trace.append(
            f"t={start}: {process.pid} runs for {duration} unit(s), ending at t={time}."
        )

        # Required boundary rule: arrivals at this timestamp join before requeue.
        enqueue_arrivals(time)
        if remaining[process.input_index] > 0:
            queue.append(process)
            trace.append(
                f"t={time}: {process.pid} has {remaining[process.input_index]} unit(s) left and rejoins the queue tail."
            )
        else:
            trace.append(f"t={time}: {process.pid} completes and is not re-enqueued.")

    return tuple(segments), tuple(trace)

