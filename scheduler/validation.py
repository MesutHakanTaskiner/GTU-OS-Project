"""Strict validation and row-to-model conversion."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from numbers import Integral
from typing import Any

from .models import ProcessSpec

MAX_PROCESSES = 100
MAX_TIME_VALUE = 100_000
MAX_TOTAL_BURST = 1_000_000


class ValidationError(ValueError):
    """Raised when simulator input is invalid."""


def _require_integer(value: Any, label: str, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValidationError(f"{label} must be an integer.")
    integer = int(value)
    if integer < minimum:
        comparison = "nonnegative" if minimum == 0 else "a positive integer"
        raise ValidationError(f"{label} must be {comparison}.")
    if integer > MAX_TIME_VALUE:
        raise ValidationError(f"{label} must not exceed {MAX_TIME_VALUE:,}.")
    return integer


def validate_processes(processes: Sequence[ProcessSpec]) -> tuple[ProcessSpec, ...]:
    if isinstance(processes, (str, bytes)) or not isinstance(processes, Sequence):
        raise ValidationError("Processes must be provided as a sequence.")
    if not processes:
        raise ValidationError("Add at least one process before running a simulation.")
    if len(processes) > MAX_PROCESSES:
        raise ValidationError(f"A workload may contain at most {MAX_PROCESSES} processes.")

    validated: list[ProcessSpec] = []
    seen_ids: set[str] = set()
    seen_indices: set[int] = set()
    total_burst = 0

    for row_number, process in enumerate(processes, start=1):
        if not isinstance(process, ProcessSpec):
            raise ValidationError(f"Row {row_number} is not a ProcessSpec.")
        if not isinstance(process.pid, str) or not process.pid.strip():
            raise ValidationError(f"Row {row_number}: Process ID must be nonempty.")
        pid = process.pid.strip()
        if pid in seen_ids:
            raise ValidationError(f"Duplicate Process ID: {pid}.")
        seen_ids.add(pid)

        arrival = _require_integer(process.arrival, f"{pid} arrival time", minimum=0)
        burst = _require_integer(process.burst, f"{pid} CPU burst", minimum=1)
        input_index = _require_integer(process.input_index, f"{pid} input index", minimum=0)
        if input_index in seen_indices:
            raise ValidationError(f"Duplicate input index: {input_index}.")
        seen_indices.add(input_index)
        total_burst += burst
        validated.append(ProcessSpec(pid, arrival, burst, input_index))

    if total_burst > MAX_TOTAL_BURST:
        raise ValidationError(
            f"Total CPU burst must not exceed {MAX_TOTAL_BURST:,} time units."
        )
    return tuple(validated)


def validate_process_rows(rows: Sequence[Mapping[str, Any]]) -> tuple[ProcessSpec, ...]:
    """Convert UI-style dictionaries to validated immutable process specs."""

    if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence):
        raise ValidationError("The process table must be a sequence of rows.")
    processes: list[ProcessSpec] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ValidationError(f"Row {index + 1} is malformed.")
        required = {"Process ID", "Arrival Time", "CPU Burst"}
        missing = required - set(row)
        if missing:
            raise ValidationError(
                f"Row {index + 1} is missing: {', '.join(sorted(missing))}."
            )
        processes.append(
            ProcessSpec(
                pid=row["Process ID"],
                arrival=row["Arrival Time"],
                burst=row["CPU Burst"],
                input_index=index,
            )
        )
    return validate_processes(processes)


def validate_quantum(quantum: Any) -> int:
    return _require_integer(quantum, "Round Robin quantum", minimum=1)

