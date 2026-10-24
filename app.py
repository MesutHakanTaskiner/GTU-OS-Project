"""Streamlit interface for the CPU Scheduling Simulator."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from scheduler import SimulationResult, ValidationError, simulate, validate_process_rows
from scheduler.simulate import ALGORITHMS
from scheduler.validation import MAX_PROCESSES, MAX_TIME_VALUE
from scheduler.verification import verify_result
from visualization import build_gantt_figure, timeline_text
from workloads.examples import table_rows

st.set_page_config(
    page_title="CPU Scheduling Simulator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f8fafc 0%, #ffffff 42%); }
    .block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 4rem; }
    .hero {
        padding: 2rem 2.1rem;
        border-radius: 22px;
        color: white;
        background: radial-gradient(circle at 90% 15%, rgba(56,189,248,.35), transparent 34%),
                    linear-gradient(130deg, #0f172a 0%, #1e3a8a 68%, #0369a1 100%);
        box-shadow: 0 18px 45px rgba(15,23,42,.16);
        margin-bottom: 1.5rem;
    }
    .hero h1 { margin: 0 0 .35rem 0; font-size: clamp(2rem, 5vw, 3.25rem); letter-spacing: -.04em; }
    .hero p { margin: 0; color: #dbeafe; max-width: 780px; font-size: 1.05rem; line-height: 1.6; }
    .eyebrow { color: #7dd3fc; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; font-size: .75rem; }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #e2e8f0; padding: 1rem 1.1rem;
        border-radius: 15px; box-shadow: 0 5px 18px rgba(15,23,42,.05);
    }
    div[data-testid="stMetricValue"] { color: #0f172a; }
    .policy-card {
        background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #2563eb;
        padding: .8rem 1rem; border-radius: 10px; color: #1e3a8a; margin: .25rem 0 1rem;
    }
    .timeline-text {
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: .88rem; line-height: 1.65; background: #0f172a; color: #e2e8f0;
        padding: 1rem 1.1rem; border-radius: 12px; overflow-x: auto;
    }
    .footnote { color: #64748b; font-size: .88rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

POLICY_DESCRIPTIONS = {
    "FCFS": "Runs the earliest-arriving ready process to completion. Arrival ties follow the original table order.",
    "SJF": "When the CPU becomes free, runs the ready process with the shortest original burst to completion.",
    "SRTF": "Always favors the shortest remaining burst, but does not preempt when the remaining times are equal.",
    "Round Robin": "Uses a FIFO ready queue and one quantum per turn. Boundary-time arrivals enter before re-enqueue.",
}


def _dataframe_for(name: str | None) -> pd.DataFrame:
    rows = table_rows(name) if name else []
    frame = pd.DataFrame(rows, columns=["Process ID", "Arrival Time", "CPU Burst"])
    frame["Process ID"] = frame["Process ID"].astype("string")
    frame["Arrival Time"] = pd.array(frame["Arrival Time"], dtype="Int64")
    frame["CPU Burst"] = pd.array(frame["CPU Burst"], dtype="Int64")
    return frame


def _load_preset(name: str | None) -> None:
    st.session_state.process_table = _dataframe_for(name)
    st.session_state.editor_generation += 1


def _raw_fingerprint(frame: pd.DataFrame, algorithm: str, quantum: Any) -> tuple[Any, ...]:
    rows = tuple(
        tuple((type(value).__name__, repr(value)) for value in row)
        for row in frame.itertuples(index=False, name=None)
    )
    return (rows, algorithm, (type(quantum).__name__, repr(quantum)))


def _metrics_frame(result: SimulationResult) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Process ID": metric.pid,
                "Arrival": metric.arrival,
                "Burst": metric.burst,
                "First Start": metric.first_start,
                "Completion": metric.completion,
                "Turnaround": metric.turnaround,
                "Waiting": metric.waiting,
                "Response": metric.response,
            }
            for metric in result.per_process_metrics
        ]
    )


if "process_table" not in st.session_state:
    st.session_state.process_table = _dataframe_for("Workload A")
if "editor_generation" not in st.session_state:
    st.session_state.editor_generation = 0
if "simulation_result" not in st.session_state:
    st.session_state.simulation_result = None
    st.session_state.simulation_processes = None
    st.session_state.simulation_fingerprint = None
    st.session_state.invariant_labels = None

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">CSE513 · Operating Systems</div>
      <h1>CPU Scheduling Simulator</h1>
      <p>Explore deterministic single-CPU scheduling with exact metrics, an interactive timeline, and a decision-by-decision trace.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Model: one CPU, one burst per process, zero-time context switches, integral time, and half-open intervals [start, end)."
)

st.subheader("1. Define the workload")
preset_a, preset_b, extra_preset, reset_column = st.columns([1, 1, 1.35, 1])
with preset_a:
    st.button("Load Workload A", width="stretch", on_click=_load_preset, args=("Workload A",))
with preset_b:
    st.button("Load Workload B", width="stretch", on_click=_load_preset, args=("Workload B",))
with extra_preset:
    selected_extra = st.selectbox(
        "Targeted example",
        ("Idle Gaps", "Simultaneous Tie", "SRTF Preemption"),
        label_visibility="collapsed",
    )
    st.button("Load targeted example", width="stretch", on_click=_load_preset, args=(selected_extra,))
with reset_column:
    st.button("Clear table", width="stretch", on_click=_load_preset, args=(None,))

edited = st.data_editor(
    st.session_state.process_table,
    key=f"process_editor_{st.session_state.editor_generation}",
    num_rows="dynamic",
    hide_index=True,
    width="stretch",
    column_config={
        "Process ID": st.column_config.TextColumn(
            "Process ID", help="A nonempty, unique identifier.", required=True
        ),
        "Arrival Time": st.column_config.NumberColumn(
            "Arrival Time", help="A nonnegative integer.", min_value=0, max_value=MAX_TIME_VALUE, step=1, format="%d"
        ),
        "CPU Burst": st.column_config.NumberColumn(
            "CPU Burst", help="A positive integer.", min_value=1, max_value=MAX_TIME_VALUE, step=1, format="%d"
        ),
    },
)
st.session_state.process_table = edited.copy()
st.caption(f"Up to {MAX_PROCESSES} processes. Row order is preserved as the final tie-breaker.")

st.subheader("2. Choose a policy")
control_left, control_right = st.columns([2.1, 1])
with control_left:
    algorithm = st.selectbox("Scheduling algorithm", ALGORITHMS, index=0)
with control_right:
    if algorithm == "Round Robin":
        quantum = st.number_input(
            "Time quantum", min_value=1, max_value=MAX_TIME_VALUE, value=2, step=1
        )
    else:
        quantum = None
        st.text_input("Time quantum", value="Only used by Round Robin", disabled=True)

st.markdown(f'<div class="policy-card">{POLICY_DESCRIPTIONS[algorithm]}</div>', unsafe_allow_html=True)

current_fingerprint = _raw_fingerprint(edited, algorithm, quantum)
run_clicked = st.button("Run Simulation", type="primary", width="stretch")

if run_clicked:
    try:
        rows = edited.to_dict(orient="records")
        processes = validate_process_rows(rows)
        result = simulate(processes, algorithm, quantum)
        invariant_labels = verify_result(processes, result)
    except ValidationError as error:
        st.error(str(error), icon="🚫")
    except AssertionError as error:
        st.error(f"Internal verification failed: {error}", icon="⚠️")
    else:
        st.session_state.simulation_result = result
        st.session_state.simulation_processes = processes
        st.session_state.simulation_fingerprint = current_fingerprint
        st.session_state.invariant_labels = invariant_labels
        st.success("Simulation completed and all required invariants passed.", icon="✅")

result = st.session_state.simulation_result
if result is not None:
    stale = st.session_state.simulation_fingerprint != current_fingerprint
    if stale:
        st.warning(
            "The workload, algorithm, or quantum has changed. The results below belong to the last simulation; run again to refresh them.",
            icon="↻",
        )

    st.subheader("3. Inspect the result")
    result_label = result.algorithm + (f" · q={result.quantum}" if result.quantum else "")
    st.caption(f"Displayed simulation: {result_label}")
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Average turnaround", f"{result.average_turnaround:.2f}")
    metric_b.metric("Average waiting", f"{result.average_waiting:.2f}")
    metric_c.metric("Average response", f"{result.average_response:.2f}")

    timeline_tab, comparison_tab, trace_tab = st.tabs(
        ["Timeline & metrics", "Compare policies", "Decision trace"]
    )
    with timeline_tab:
        st.plotly_chart(build_gantt_figure(result), width="stretch", config={"displaylogo": False})
        st.markdown("**Accessible execution order**")
        st.markdown(f'<div class="timeline-text">{timeline_text(result)}</div>', unsafe_allow_html=True)
        st.markdown("**Per-process metrics**")
        st.dataframe(_metrics_frame(result), hide_index=True, width="stretch")
        checks = ", ".join(st.session_state.invariant_labels)
        st.caption(f"Verified: {checks}.")

    with comparison_tab:
        compare_rows = []
        for policy in ALGORITHMS:
            comparison = simulate(
                st.session_state.simulation_processes,
                policy,
                result.quantum or 2 if policy == "Round Robin" else None,
            )
            compare_rows.append(
                {
                    "Algorithm": policy,
                    "Quantum": str(comparison.quantum) if comparison.quantum else "—",
                    "Avg. Turnaround": comparison.average_turnaround,
                    "Avg. Waiting": comparison.average_waiting,
                    "Avg. Response": comparison.average_response,
                    "Finish Time": comparison.segments[-1].end,
                }
            )
        comparison_frame = pd.DataFrame(compare_rows)
        st.dataframe(
            comparison_frame.style.format(
                {"Avg. Turnaround": "{:.2f}", "Avg. Waiting": "{:.2f}", "Avg. Response": "{:.2f}"}
            ),
            hide_index=True,
            width="stretch",
        )
        st.caption("Round Robin uses the displayed simulation quantum, or q=2 when the displayed policy is not Round Robin.")

    with trace_tab:
        for event in result.decision_trace:
            st.markdown(f"- {event}")

st.divider()
st.markdown(
    '<p class="footnote">This educational simulator demonstrates scheduling policies; it does not reproduce the actual Ubuntu scheduler.</p>',
    unsafe_allow_html=True,
)

