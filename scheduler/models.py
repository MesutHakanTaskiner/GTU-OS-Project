"""Immutable data models shared by the scheduling algorithms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class ProcessSpec:
    """A single process with one CPU burst."""

    pid: str
    arrival: int
    burst: int
    input_index: int


@dataclass(frozen=True, slots=True)
class ExecutionSegment:
    """A half-open CPU interval [start, end); pid=None means IDLE."""

    pid: Optional[str]
    start: int
    end: int
    slice_index: Optional[int] = None

    @property
    def duration(self) -> int:
        return self.end - self.start


@dataclass(frozen=True, slots=True)
class ProcessMetrics:
    pid: str
    arrival: int
    burst: int
    first_start: int
    completion: int
    turnaround: int
    waiting: int
    response: int


@dataclass(frozen=True, slots=True)
class SimulationResult:
    algorithm: str
    quantum: Optional[int]
    segments: tuple[ExecutionSegment, ...]
    per_process_metrics: tuple[ProcessMetrics, ...]
    average_turnaround: float
    average_waiting: float
    average_response: float
    decision_trace: tuple[str, ...]

