import subprocess
import time
import requests
import sys
import os
import signal

def run_system_test():
    print("Starting System Integration Test...")
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    solver_dir = os.path.join(project_root, "solver")
    gateway_dir = os.path.join(project_root, "gateway")

    # 1. Start Python Solver
    print("Starting Python Solver...")
    solver_proc = subprocess.Popen(
        "/home/hubertkuch/Przestrzenie/Praca/.local/bin/uv run python main.py",
        cwd=solver_dir,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # 2. Start Go Gateway
    print("Starting Go Gateway...")
    gateway_proc = subprocess.Popen(
        "/bin/go run .",
        cwd=gateway_dir,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    time.sleep(10)

    # 3. Perform Request
    url = "http://localhost:8085/api/simulation"
    payload = {
        "location": {
            "latitude": 52.2297,
            "longitude": 21.0122,
            "tz": "Europe/Warsaw",
            "altitude": 100
        },
        "system_config": {
            "arrays": [
                {
                    "surface_tilt": 30,
                    "surface_azimuth": 180,
                    "modules_per_string": 10,
                    "strings": 2,
                    "panel": {
                        "pdc0": 300,
                        "v_mp": 30,
                        "i_mp": 10,
                        "v_oc": 37,
                        "i_sc": 11,
                        "gamma_pdc": -0.004,
                        "alpha_sc": 0.005,
                        "beta_voc": -0.11,
                        "cells_in_series": 60
                    }
                }
            ],
            "inverter": {
                "pdc0": 5000,
                "eta_inv_nom": 0.96,
                "v_dc_max": 1000
            }
        },
        "date": "2026-06-21"
    }

    success = False
    try:
        print(f"Sending POST request to {url}...")
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            ac_output = data.get("ac_output", [])
            if len(ac_output) == 24 and sum(ac_output) > 0:
                print(f"SUCCESS: Total AC Energy: {sum(ac_output):.2f}")
                success = True
            else:
                print(f"FAILURE: Data validation failed. Output length: {len(ac_output)}, Sum: {sum(ac_output)}")
        else:
            print(f"FAILURE: HTTP {response.status_code} - {response.text}")

        # 4. Test /api/solve
        solve_url = "http://localhost:8085/api/solve"
        solve_payload = {
            "panel": {
                "pdc0": 300,
                "v_mp": 30,
                "i_mp": 10,
                "v_oc": 37,
                "i_sc": 11,
                "gamma_pdc": -0.004,
                "alpha_sc": 0.005,
                "beta_voc": -0.11,
                "cells_in_series": 60
            },
            "inverter": {
                "pdc0": 5000,
                "eta_inv_nom": 0.96,
                "v_dc_max": 1000
            },
            "modules_per_string": 10,
            "strings": 2,
            "surface_tilt": 30,
            "surface_azimuth": 180,
            "duration": "24h",
            "when": "2026-06-21T00:00:00Z",
            "temperature": 25.0,
            "location": {
                "latitude": 52.2297,
                "longitude": 21.0122,
                "tz": "Europe/Warsaw",
                "altitude": 100
            }
        }
        print(f"Sending POST request to {solve_url}...")
        solve_response = requests.post(solve_url, json=solve_payload, timeout=15)
        if solve_response.status_code == 200:
            print("SUCCESS: /api/solve responded correctly")
        else:
            print(f"FAILURE: /api/solve HTTP {solve_response.status_code} - {solve_response.text}")
            success = False
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        print("Cleaning up...")
        os.killpg(os.getpgid(solver_proc.pid), signal.SIGTERM)
        os.killpg(os.getpgid(gateway_proc.pid), signal.SIGTERM)
        
        if not success:
            print("\n--- Solver Stdout ---")
            print(solver_proc.stdout.read().decode('utf-8'))
            print("--- Solver Stderr ---")
            print(solver_proc.stderr.read().decode('utf-8'))
            print("\n--- Gateway Stdout ---")
            print(gateway_proc.stdout.read().decode('utf-8'))
            print("--- Gateway Stderr ---")
            print(gateway_proc.stderr.read().decode('utf-8'))
        
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    run_system_test()
