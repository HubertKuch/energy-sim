import subprocess
import time
import requests
import os
import signal
import pytest

@pytest.fixture(scope="module")
def solar_system():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    solver_dir = os.path.join(project_root, "solver")
    gateway_dir = os.path.join(project_root, "gateway")

    # Start processes
    solver_proc = subprocess.Popen(
        "/home/hubertkuch/Przestrzenie/Praca/.local/bin/uv run python main.py",
        cwd=solver_dir, shell=True, preexec_fn=os.setsid
    )
    gateway_proc = subprocess.Popen(
        "/bin/go run .",
        cwd=gateway_dir, shell=True, preexec_fn=os.setsid
    )

    time.sleep(10) # Wait for startup
    yield "http://localhost:8085"

    # Cleanup
    os.killpg(os.getpgid(solver_proc.pid), signal.SIGTERM)
    os.killpg(os.getpgid(gateway_proc.pid), signal.SIGTERM)

def test_invalid_date(solar_system):
    url = f"{solar_system}/api/simulation"
    payload = {"date": "invalid-date"}
    response = requests.post(url, json=payload)
    assert response.status_code == 400

def test_solve_night(solar_system):
    url = f"{solar_system}/api/solve"
    payload = {
        "panel": {"pdc0": 300, "v_mp": 30, "i_mp": 10, "v_oc": 37, "i_sc": 11, "gamma_pdc": -0.004, "alpha_sc": 0.005, "beta_voc": -0.11, "cells_in_series": 60},
        "inverter": {"pdc0": 5000, "eta_inv_nom": 0.96, "v_dc_max": 1000},
        "modules_per_string": 10,
        "strings": 2,
        "duration": "1h",
        "when": "2026-06-21T00:00:00Z", # Midnight
        "temperature": 25.0,
        "location": {"latitude": 52.2, "longitude": 21.0, "tz": "Europe/Warsaw"}
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert sum(data['ac_output']) == 0

def test_extreme_temperature(solar_system):
    url = f"{solar_system}/api/solve"
    payload = {
        "panel": {"pdc0": 300, "v_mp": 30, "i_mp": 10, "v_oc": 37, "i_sc": 11, "gamma_pdc": -0.004, "alpha_sc": 0.005, "beta_voc": -0.11, "cells_in_series": 60},
        "inverter": {"pdc0": 5000, "eta_inv_nom": 0.96, "v_dc_max": 1000},
        "modules_per_string": 10,
        "strings": 2,
        "duration": "1h",
        "when": "2026-06-21T12:00:00Z",
        "temperature": 100.0, # Very hot
        "location": {"latitude": 52.2, "longitude": 21.0, "tz": "Europe/Warsaw"}
    }
    response_hot = requests.post(url, json=payload)
    
    payload["temperature"] = -50.0 # Very cold
    response_cold = requests.post(url, json=payload)
    
    assert response_hot.status_code == 200
    assert response_cold.status_code == 200
    
    # Cold panels usually perform better than hot ones
    assert sum(response_cold.json()['ac_output']) > sum(response_hot.json()['ac_output'])
