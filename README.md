# CPU Scheduling Simulator

A deterministic, browser-based teaching simulator for four classic single-CPU scheduling policies:

- First-Come, First-Served (FCFS)
- Non-preemptive Shortest Job First (SJF)
- Preemptive Shortest Remaining Time First (SRTF)
- Round Robin (RR)

The application uses Python for pure scheduling logic, Streamlit for the interface, and Plotly for an interactive Gantt chart. It models scheduling policies for an educational workload; it does **not** reproduce the actual Ubuntu scheduler.

## Features

- Editable process table with stable input-order tie-breaking
- Professor Workload A/B presets and three targeted regression presets
- Strict validation for IDs, integral arrival/burst/quantum values, bounds, and malformed rows
- Explicit `IDLE` intervals and half-open `[start, end)` timeline semantics
- Visible, unmerged RR quantum boundaries, including consecutive slices of one process
- Eight per-process fields and exact internally computed averages
- Accessible textual timeline and policy decision trace
- Side-by-side comparison of all four policies
- Independent invariant verification after every UI simulation
- 61 automated tests, including the eight required professor workload combinations

## Requirements

- Python 3.11 (the locally verified version)
- A modern browser

No login, database, API key, or persistent runtime storage is required.

## Run locally

### Windows PowerShell

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

### macOS or Linux

```bash
python3.11 -m venv venv
source venv/bin/activate
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

Open `http://localhost:8501`, load a preset or edit the table, select a policy, and click **Run Simulation**.

## Test

```bash
python -m pytest -q
```

Verified locally on 24 October 2026 with Python 3.11.0:

```text
61 passed in 1.36s
```

The suite contains independent expected timelines and metrics, strict validation checks, an application smoke test, and these invariants:

1. Each process receives exactly its declared burst time.
2. No process executes before arrival.
3. The one-CPU timeline is contiguous and non-overlapping.
4. Waiting and response times are nonnegative.
5. The CPU never idles while an arrived, unfinished process exists.

## Architecture

```text
app.py                    Streamlit UI and state management
scheduler/                Pure models, policies, metrics, validation, verification
visualization/gantt.py    Interactive Plotly timeline
workloads/examples.py     Required and targeted workload presets
tests/                    Independent oracle, regression, validation, invariant, UI tests
report/                   Editable report source and PDF build script
deliverables/             Final report PDF and source ZIP
```

The stable public API is:

```python
from scheduler import ProcessSpec, simulate

processes = (
    ProcessSpec("P1", arrival=0, burst=5, input_index=0),
    ProcessSpec("P2", arrival=2, burst=1, input_index=1),
)
result = simulate(processes, "SRTF")
```

## Deterministic policy rules

- All times are integral and all intervals are half-open.
- A ready process always prevents the CPU from idling.
- Ties use arrival time and then immutable original input index.
- SJF considers only ready processes and never preempts.
- SRTF preempts only for a **strictly** shorter remaining time; an equal remaining time keeps the running process.
- RR appends arrivals at an exact quantum boundary before re-enqueuing the unfinished running process.

## Deployment

The repository is prepared for Streamlit Community Cloud with root-level `app.py` and pinned runtime dependencies in `requirements.txt`. See [DEPLOYMENT.md](DEPLOYMENT.md) for the verified status and the exact owner-facing deployment path.

Official references:

- [Deploy an app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [Share an app](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app)

## Report and source package

- `deliverables/CSE513_Assignment1_Report.pdf`
- `deliverables/cpu-scheduling-simulator-source.zip`
- `report/report_source.md` (editable report content)
- `report/HAND_CALCULATIONS_GUIDE.md` (copy-ready independent calculation steps)
- `REQUIREMENTS_AUDIT.md` (evidence-based completion and remaining-work checklist)

The authoritative `CSE513-Assignment-1.pdf` was reviewed in full after implementation. Its four pages match the implemented algorithm rules, website requirements, required workloads, test obligations, analysis questions, AI disclosure, and submission format; no conflict with the working `AGENTS.md` specification was found.

