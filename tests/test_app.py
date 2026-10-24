"""Streamlit smoke coverage for the default teaching workflow."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_default_workload_a_fcfs_runs_without_ui_exception():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py")
    app.run(timeout=20)
    assert not app.exception

    run_button = next(button for button in app.button if button.label == "Run Simulation")
    run_button.click().run(timeout=20)

    assert not app.exception
    assert app.success[0].value.startswith("Simulation completed")
    assert [(metric.label, metric.value) for metric in app.metric] == [
        ("Average turnaround", "10.50"),
        ("Average waiting", "6.75"),
        ("Average response", "6.75"),
    ]

