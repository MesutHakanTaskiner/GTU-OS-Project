"""Internal helpers used by multiple schedulers."""

from __future__ import annotations

from .models import ExecutionSegment


def append_segment(
    segments: list[ExecutionSegment],
    pid: str | None,
    start: int,
    end: int,
    *,
    merge_adjacent: bool,
    slice_index: int | None = None,
) -> None:
    if end <= start:
        raise ValueError("Execution segments must have positive duration.")
    if (
        merge_adjacent
        and segments
        and segments[-1].pid == pid
        and segments[-1].end == start
        and segments[-1].slice_index is None
        and slice_index is None
    ):
        previous = segments[-1]
        segments[-1] = ExecutionSegment(pid, previous.start, end)
        return
    segments.append(ExecutionSegment(pid, start, end, slice_index))

