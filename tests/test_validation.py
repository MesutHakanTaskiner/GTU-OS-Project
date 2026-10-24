"""Strict input validation checks."""

from __future__ import annotations

import math

import pytest

from scheduler import ProcessSpec, ValidationError, simulate, validate_process_rows
from scheduler.validation import MAX_PROCESSES, MAX_TIME_VALUE


@pytest.mark.parametrize(
    "rows",
    [
        [],
        [{"Process ID": "", "Arrival Time": 0, "CPU Burst": 1}],
        [{"Process ID": "   ", "Arrival Time": 0, "CPU Burst": 1}],
        [
            {"Process ID": "P", "Arrival Time": 0, "CPU Burst": 1},
            {"Process ID": "P", "Arrival Time": 1, "CPU Burst": 1},
        ],
        [{"Process ID": "P", "Arrival Time": -1, "CPU Burst": 1}],
        [{"Process ID": "P", "Arrival Time": 0, "CPU Burst": 0}],
        [{"Process ID": "P", "Arrival Time": 0, "CPU Burst": -2}],
        [{"Process ID": "P", "Arrival Time": 0.0, "CPU Burst": 1}],
        [{"Process ID": "P", "Arrival Time": 0, "CPU Burst": 1.5}],
        [{"Process ID": "P", "Arrival Time": True, "CPU Burst": 1}],
        [{"Process ID": "P", "Arrival Time": "0", "CPU Burst": 1}],
        [{"Process ID": "P", "Arrival Time": math.nan, "CPU Burst": 1}],
        [{"Process ID": "P", "Arrival Time": 0}],
        ["malformed"],
    ],
)
def test_invalid_rows_are_rejected(rows):
    with pytest.raises(ValidationError):
        validate_process_rows(rows)


@pytest.mark.parametrize("quantum", [None, 0, -1, 1.0, True, "2", math.nan])
def test_invalid_rr_quantum_is_rejected(quantum):
    with pytest.raises(ValidationError):
        simulate((ProcessSpec("P", 0, 1, 0),), "Round Robin", quantum)


def test_unknown_algorithm_is_rejected():
    with pytest.raises(ValidationError):
        simulate((ProcessSpec("P", 0, 1, 0),), "Priority")


def test_realistic_limits_are_enforced():
    too_many = [
        {"Process ID": f"P{i}", "Arrival Time": 0, "CPU Burst": 1}
        for i in range(MAX_PROCESSES + 1)
    ]
    with pytest.raises(ValidationError, match="at most"):
        validate_process_rows(too_many)
    with pytest.raises(ValidationError, match="must not exceed"):
        validate_process_rows(
            [{"Process ID": "P", "Arrival Time": MAX_TIME_VALUE + 1, "CPU Burst": 1}]
        )

