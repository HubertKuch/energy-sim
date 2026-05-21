import pytest
from types import SimpleNamespace
import pandas as pd
from solar_solver.engine import solve_solar

def test_solve_solar_basic():
    # Mocking the expanded gRPC request
    request = SimpleNamespace(
        location=SimpleNamespace(
            latitude=52.2297,
            longitude=21.0122,
            tz='Europe/Warsaw',
            altitude=100
        ),
        system_config=SimpleNamespace(
            arrays=[
                SimpleNamespace(
                    surface_tilt=30,
                    surface_azimuth=180,
                    modules_per_string=10,
                    strings=2,
                    module_parameters=SimpleNamespace(
                        pdc0=300,
                        v_mp=30,
                        i_mp=10,
                        v_oc=37,
                        i_sc=11,
                        gamma_pdc=-0.004,
                        alpha_sc=0.005,
                        beta_voc=-0.11,
                        cells_in_series=60
                    )
                )
            ],
            inverter_parameters=SimpleNamespace(
                pdc0=5000,
                eta_inv_nom=0.96,
                v_dc_max=1000
            )
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
    assert results.iloc[0] > 0
