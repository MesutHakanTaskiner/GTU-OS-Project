"""Interactive, single-lane CPU Gantt chart."""

from __future__ import annotations

import plotly.graph_objects as go

from scheduler.models import SimulationResult

PROCESS_COLORS = (
    "#2563EB",
    "#7C3AED",
    "#059669",
    "#EA580C",
    "#DB2777",
    "#0891B2",
    "#65A30D",
    "#9333EA",
    "#DC2626",
    "#4F46E5",
)
IDLE_COLOR = "#94A3B8"


def build_gantt_figure(result: SimulationResult) -> go.Figure:
    process_ids = [metric.pid for metric in result.per_process_metrics]
    colors = {pid: PROCESS_COLORS[index % len(PROCESS_COLORS)] for index, pid in enumerate(process_ids)}
    colors["IDLE"] = IDLE_COLOR
    seen: set[str] = set()
    figure = go.Figure()

    for segment in result.segments:
        label = segment.pid or "IDLE"
        duration = segment.end - segment.start
        slice_text = (
            f"<br>RR slice #{segment.slice_index}" if segment.slice_index is not None else ""
        )
        figure.add_trace(
            go.Bar(
                x=[duration],
                y=["CPU"],
                base=[segment.start],
                orientation="h",
                name=label,
                legendgroup=label,
                showlegend=label not in seen,
                marker={
                    "color": colors[label],
                    "line": {"color": "#FFFFFF", "width": 3 if result.algorithm == "Round Robin" else 1.5},
                },
                text=[label],
                textposition="inside",
                insidetextanchor="middle",
                textfont={"color": "white", "size": 14},
                customdata=[[segment.start, segment.end, duration]],
                hovertemplate=(
                    f"<b>{label}</b>{slice_text}<br>Start: %{{customdata[0]}}"
                    "<br>End: %{customdata[1]}<br>Duration: %{customdata[2]}<extra></extra>"
                ),
            )
        )
        seen.add(label)

    boundaries = sorted({value for segment in result.segments for value in (segment.start, segment.end)})
    for boundary in boundaries:
        figure.add_vline(x=boundary, line_width=1, line_color="rgba(15, 23, 42, 0.20)")

    final_time = result.segments[-1].end
    figure.update_layout(
        barmode="overlay",
        height=285,
        margin={"l": 25, "r": 20, "t": 25, "b": 35},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,250,252,0.8)",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.05, "xanchor": "left", "x": 0},
        xaxis={
            "title": "Time",
            "tickmode": "array",
            "tickvals": boundaries,
            "range": [0, final_time],
            "fixedrange": False,
            "gridcolor": "rgba(148,163,184,0.20)",
            "zeroline": False,
        },
        yaxis={"title": None, "fixedrange": True, "showgrid": False},
        hoverlabel={"bgcolor": "white", "font_size": 13},
    )
    return figure


def timeline_text(result: SimulationResult) -> str:
    parts = []
    for segment in result.segments:
        label = segment.pid or "IDLE"
        suffix = f" / slice {segment.slice_index}" if segment.slice_index is not None else ""
        parts.append(f"{label} [{segment.start}, {segment.end}){suffix}")
    return " -> ".join(parts)

