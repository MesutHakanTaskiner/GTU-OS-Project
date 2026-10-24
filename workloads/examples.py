"""Professor-provided and targeted regression workloads."""

from __future__ import annotations

from scheduler.models import ProcessSpec

WORKLOAD_A = (
    ("P1", 0, 8),
    ("P2", 1, 4),
    ("P3", 2, 2),
    ("P4", 4, 1),
)

WORKLOAD_B = (
    ("P1", 2, 3),
    ("P2", 2, 1),
    ("P3", 8, 2),
    ("P4", 9, 1),
)

IDLE_GAPS = (("I1", 2, 2), ("I2", 6, 1))
SIMULTANEOUS_TIE = (("T1", 0, 3), ("T2", 0, 1), ("T3", 0, 1))
SRTF_PREEMPTION = (("E1", 0, 5), ("E2", 1, 4), ("E3", 2, 1))

PRESETS = {
    "Workload A": WORKLOAD_A,
    "Workload B": WORKLOAD_B,
    "Idle Gaps": IDLE_GAPS,
    "Simultaneous Tie": SIMULTANEOUS_TIE,
    "SRTF Preemption": SRTF_PREEMPTION,
}


def process_specs(name: str) -> tuple[ProcessSpec, ...]:
    return tuple(
        ProcessSpec(pid, arrival, burst, index)
        for index, (pid, arrival, burst) in enumerate(PRESETS[name])
    )


def table_rows(name: str) -> list[dict[str, int | str]]:
    return [
        {"Process ID": pid, "Arrival Time": arrival, "CPU Burst": burst}
        for pid, arrival, burst in PRESETS[name]
    ]

