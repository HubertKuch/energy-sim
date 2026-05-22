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

def test_battery_storage_logic(solar_system):
    url = f"{solar_system}/api/solve"
    
    # 24 hours load of 2kW constant
    load_profile = [2.0] * 24
    
    payload = {
        "panel": {"pdc0": 300, "v_mp": 30, "i_mp": 10, "v_oc": 37, "i_sc": 11, "gamma_pdc": -0.004, "alpha_sc": 0.005, "beta_voc": -0.11, "cells_in_series": 60},
        "inverter": {"pdc0": 5000, "eta_inv_nom": 0.96, "v_dc_max": 1000},
        "battery": {
            "capacity_kwh": 10.0,
            "max_charge_kw": 5.0,
            "max_discharge_kw": 5.0,
            "efficiency": 0.95,
            "initial_soc_kwh": 5.0
        },
        "modules_per_string": 10,
        "strings": 4, # ~12kWp system, should have excess during day
        "surface_tilt": 30,
        "surface_azimuth": 180,
        "duration": "24h",
        "when": "2026-06-21T00:00:00Z",
        "temperature": 25.0,
        "location": {"latitude": 52.2, "longitude": 21.0, "tz": "Europe/Warsaw"},
        "load_profile_kw": load_profile
    }
    
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check if battery SOC changed
    soc = data.get('battery_soc_kwh', [])
    assert len(soc) == 24
    assert any(s != 5.0 for s in soc)
    
    # Check grid interactions
    grid_import = data.get('grid_import_kw', [])
    grid_export = data.get('grid_export_kw', [])
    assert len(grid_import) == 24
    assert len(grid_export) == 24
    
    print(f"Final SOC: {soc[-1]:.2f} kWh")
    print(f"Total Grid Import: {sum(grid_import):.2f} kWh")
    print(f"Total Grid Export: {sum(grid_export):.2f} kWh")
