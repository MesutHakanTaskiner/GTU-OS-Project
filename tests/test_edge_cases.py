"""Targeted regressions for policy-specific boundary rules."""

from scheduler import ProcessSpec, simulate
from workloads.examples import process_specs


def compact(result):
    return [(segment.pid, segment.start, segment.end) for segment in result.segments]


def test_initial_and_middle_idle_intervals():
    result = simulate(process_specs("Idle Gaps"), "FCFS")
    assert compact(result) == [(None, 0, 2), ("I1", 2, 4), (None, 4, 6), ("I2", 6, 7)]
    assert all(metric.waiting == metric.response == 0 for metric in result.per_process_metrics)


def test_sjf_simultaneous_equal_bursts_use_input_order():
    result = simulate(process_specs("Simultaneous Tie"), "SJF")
    assert compact(result) == [("T2", 0, 1), ("T3", 1, 2), ("T1", 2, 5)]


def test_sjf_does_not_preempt_for_later_short_job():
    processes = (ProcessSpec("Long", 0, 5, 0), ProcessSpec("Short", 1, 1, 1))
    result = simulate(processes, "SJF")
    assert compact(result) == [("Long", 0, 5), ("Short", 5, 6)]


def test_srtf_keeps_current_on_equal_remaining_then_preempts_for_strictly_shorter():
    result = simulate(process_specs("SRTF Preemption"), "SRTF")
    assert compact(result) == [("E1", 0, 2), ("E3", 2, 3), ("E1", 3, 6), ("E2", 6, 10)]


def test_srtf_tie_when_selecting_new_process_uses_arrival_then_input_order():
    processes = (
        ProcessSpec("A", 0, 1, 0),
        ProcessSpec("B", 1, 2, 1),
        ProcessSpec("C", 1, 2, 2),
    )
    result = simulate(processes, "SRTF")
    assert compact(result) == [("A", 0, 1), ("B", 1, 3), ("C", 3, 5)]


def test_rr_arrival_at_quantum_boundary_precedes_requeue():
    processes = (ProcessSpec("B1", 0, 4, 0), ProcessSpec("B2", 2, 1, 1))
    result = simulate(processes, "Round Robin", 2)
    assert compact(result) == [("B1", 0, 2), ("B2", 2, 3), ("B1", 3, 5)]


def test_rr_only_ready_process_keeps_separate_slices():
    result = simulate((ProcessSpec("Solo", 0, 5, 0),), "Round Robin", 2)
    assert compact(result) == [("Solo", 0, 2), ("Solo", 2, 4), ("Solo", 4, 5)]
    assert [segment.slice_index for segment in result.segments] == [1, 2, 3]


def test_completion_exactly_at_arrival_boundary():
    processes = (ProcessSpec("A", 0, 2, 0), ProcessSpec("B", 2, 1, 1))
    assert compact(simulate(processes, "FCFS")) == [("A", 0, 2), ("B", 2, 3)]

