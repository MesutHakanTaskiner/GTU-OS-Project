"""Cross-algorithm invariant checks independent of selection logic."""

import pytest

from scheduler import simulate
from scheduler.verification import verify_result
from workloads.examples import PRESETS, process_specs


@pytest.mark.parametrize("workload", list(PRESETS))
@pytest.mark.parametrize("algorithm", ["FCFS", "SJF", "SRTF", "Round Robin"])
def test_all_presets_satisfy_required_invariants(workload, algorithm):
    processes = process_specs(workload)
    result = simulate(processes, algorithm, 2 if algorithm == "Round Robin" else None)
    labels = verify_result(processes, result)
    assert len(labels) == 5


def test_rr_quantum_comparison_workload_a():
    processes = process_specs("Workload A")
    expected = {
        1: (8.5, 4.75, 0.75),
        2: (8.5, 4.75, 1.75),
        4: (9.25, 5.5, 3.75),
    }
    for quantum, averages in expected.items():
        result = simulate(processes, "Round Robin", quantum)
        assert (
            result.average_turnaround,
            result.average_waiting,
            result.average_response,
        ) == averages

