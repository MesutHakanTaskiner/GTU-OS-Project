"""Independent invariant checks for completed simulation results."""

from __future__ import annotations

from collections import Counter

from .models import ProcessSpec, SimulationResult


def verify_result(processes: tuple[ProcessSpec, ...], result: SimulationResult) -> tuple[str, ...]:
    """Raise AssertionError on an invariant violation and return check labels."""

    assert result.segments, "Timeline must not be empty."
    assert result.segments[0].start == 0, "Timeline must begin at time zero."

    for previous, current in zip(result.segments, result.segments[1:]):
        assert previous.end == current.start, "Timeline must be contiguous and non-overlapping."
    for segment in result.segments:
        assert segment.start < segment.end, "Segments must have positive duration."

    executed = Counter()
    process_by_id = {process.pid: process for process in processes}
    for segment in result.segments:
        if segment.pid is not None:
            assert segment.pid in process_by_id, "Timeline contains an unknown process."
            process = process_by_id[segment.pid]
            assert segment.start >= process.arrival, "A process executed before arrival."
            executed[segment.pid] += segment.duration
    for process in processes:
        assert executed[process.pid] == process.burst, "CPU time does not equal burst."

    metrics_by_id = {metric.pid: metric for metric in result.per_process_metrics}
    for process in processes:
        metric = metrics_by_id[process.pid]
        assert metric.turnaround == metric.completion - process.arrival
        assert metric.waiting == metric.turnaround - process.burst
        assert metric.response == metric.first_start - process.arrival
        assert metric.waiting >= 0 and metric.response >= 0

    for idle in (segment for segment in result.segments if segment.pid is None):
        for process in processes:
            completion = metrics_by_id[process.pid].completion
            overlap = max(idle.start, process.arrival) < min(idle.end, completion)
            assert not overlap, "CPU idled while an arrived process was unfinished."

    assert result.segments[-1].end == max(
        metric.completion for metric in result.per_process_metrics
    )
    return (
        "burst accounting",
        "arrival safety",
        "single-CPU continuity",
        "nonnegative waiting/response",
        "work-conserving CPU",
    )

