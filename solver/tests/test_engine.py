import pytest
from types import SimpleNamespace
import pandas as pd
from solar_solver.engine import solve_solar

def test_solve_solar_basic():
    # Mocking the gRPC request using SimpleNamespace for brevity in tests
    request = SimpleNamespace(
        location=SimpleNamespace(
            latitude=52.2297,
            longitude=21.0122,
            tz='Europe/Warsaw',
            altitude=100
        ),
        system_config=SimpleNamespace(
            surface_tilt=30,
            surface_azimuth=180,
            module_parameters=SimpleNamespace(pdc0=300, gamma_pdc=-0.004),
            inverter_parameters=SimpleNamespace(pdc0=5000, eta_inv_nom=0.96)
        ),
        weather=[
            SimpleNamespace(
                timestamp='2026-06-21 12:00:00',
                ghi=1000,
                dni=800,
                dhi=200,
                temp_air=25,
                wind_speed=2
            )
        ]
    )

    results = solve_solar(request)
    
    assert isinstance(results, pd.Series)
    assert len(results) == 1
    assert results.iloc[0] > 0  # Should produce power at noon
