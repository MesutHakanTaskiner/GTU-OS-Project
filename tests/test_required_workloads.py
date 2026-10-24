"""Independent expected outcomes for both professor workloads."""

from __future__ import annotations

import pytest

from scheduler import simulate
from workloads.examples import process_specs


def timeline(result):
    return [(segment.pid or "IDLE", segment.start, segment.end) for segment in result.segments]


def metrics(result):
    return {
        item.pid: (
            item.first_start,
            item.completion,
            item.turnaround,
            item.waiting,
            item.response,
        )
        for item in result.per_process_metrics
    }


@pytest.mark.parametrize(
    ("algorithm", "quantum", "expected_timeline", "expected_metrics", "averages"),
    [
        (
            "FCFS",
            None,
            [("P1", 0, 8), ("P2", 8, 12), ("P3", 12, 14), ("P4", 14, 15)],
            {"P1": (0, 8, 8, 0, 0), "P2": (8, 12, 11, 7, 7), "P3": (12, 14, 12, 10, 10), "P4": (14, 15, 11, 10, 10)},
            (10.5, 6.75, 6.75),
        ),
        (
            "SJF",
            None,
            [("P1", 0, 8), ("P4", 8, 9), ("P3", 9, 11), ("P2", 11, 15)],
            {"P1": (0, 8, 8, 0, 0), "P2": (11, 15, 14, 10, 10), "P3": (9, 11, 9, 7, 7), "P4": (8, 9, 5, 4, 4)},
            (9.0, 5.25, 5.25),
        ),
        (
            "SRTF",
            None,
            [("P1", 0, 1), ("P2", 1, 2), ("P3", 2, 4), ("P4", 4, 5), ("P2", 5, 8), ("P1", 8, 15)],
            {"P1": (0, 15, 15, 7, 0), "P2": (1, 8, 7, 3, 0), "P3": (2, 4, 2, 0, 0), "P4": (4, 5, 1, 0, 0)},
            (6.25, 2.5, 0.0),
        ),
        (
            "Round Robin",
            2,
            [("P1", 0, 2), ("P2", 2, 4), ("P3", 4, 6), ("P1", 6, 8), ("P4", 8, 9), ("P2", 9, 11), ("P1", 11, 13), ("P1", 13, 15)],
            {"P1": (0, 15, 15, 7, 0), "P2": (2, 11, 10, 6, 1), "P3": (4, 6, 4, 2, 2), "P4": (8, 9, 5, 4, 4)},
            (8.5, 4.75, 1.75),
        ),
    ],
)
def test_workload_a(algorithm, quantum, expected_timeline, expected_metrics, averages):
    result = simulate(process_specs("Workload A"), algorithm, quantum)
    assert timeline(result) == expected_timeline
    assert metrics(result) == expected_metrics
    assert (result.average_turnaround, result.average_waiting, result.average_response) == averages


@pytest.mark.parametrize(
    ("algorithm", "quantum", "expected_timeline", "expected_metrics", "averages"),
    [
        (
            "FCFS",
            None,
            [("IDLE", 0, 2), ("P1", 2, 5), ("P2", 5, 6), ("IDLE", 6, 8), ("P3", 8, 10), ("P4", 10, 11)],
            {"P1": (2, 5, 3, 0, 0), "P2": (5, 6, 4, 3, 3), "P3": (8, 10, 2, 0, 0), "P4": (10, 11, 2, 1, 1)},
            (2.75, 1.0, 1.0),
        ),
        (
            "SJF",
            None,
            [("IDLE", 0, 2), ("P2", 2, 3), ("P1", 3, 6), ("IDLE", 6, 8), ("P3", 8, 10), ("P4", 10, 11)],
            {"P1": (3, 6, 4, 1, 1), "P2": (2, 3, 1, 0, 0), "P3": (8, 10, 2, 0, 0), "P4": (10, 11, 2, 1, 1)},
            (2.25, 0.5, 0.5),
        ),
        (
            "SRTF",
            None,
            [("IDLE", 0, 2), ("P2", 2, 3), ("P1", 3, 6), ("IDLE", 6, 8), ("P3", 8, 10), ("P4", 10, 11)],
            {"P1": (3, 6, 4, 1, 1), "P2": (2, 3, 1, 0, 0), "P3": (8, 10, 2, 0, 0), "P4": (10, 11, 2, 1, 1)},
            (2.25, 0.5, 0.5),
        ),
        (
            "Round Robin",
            2,
            [("IDLE", 0, 2), ("P1", 2, 4), ("P2", 4, 5), ("P1", 5, 6), ("IDLE", 6, 8), ("P3", 8, 10), ("P4", 10, 11)],
            {"P1": (2, 6, 4, 1, 0), "P2": (4, 5, 3, 2, 2), "P3": (8, 10, 2, 0, 0), "P4": (10, 11, 2, 1, 1)},
            (2.75, 1.0, 0.75),
        ),
    ],
)
def test_workload_b(algorithm, quantum, expected_timeline, expected_metrics, averages):
    result = simulate(process_specs("Workload B"), algorithm, quantum)
    assert timeline(result) == expected_timeline
    assert metrics(result) == expected_metrics
    assert (result.average_turnaround, result.average_waiting, result.average_response) == averages

