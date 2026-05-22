import pytest
import pandas as pd
from types import SimpleNamespace
from solar_solver.engine import (
    SolarPanel, SolarInverter, SolarArray, SolarSystem,
    parse_location, parse_system, solve
)

@pytest.fixture
def sample_panel():
    return SolarPanel(
        pdc0=300, v_mp=30, i_mp=10, v_oc=37, i_sc=11,
        gamma_pdc=-0.004, alpha_sc=0.005, beta_voc=-0.11, cells_in_series=60
    )

@pytest.fixture
def sample_inverter():
    return SolarInverter(pdc0=5000, eta_inv_nom=0.96, v_dc_max=1000)

def test_solar_panel_to_pvlib(sample_panel):
    d = sample_panel.to_pvlib_dict()
    assert d['pdc0'] == 300
    assert d['v_mp'] == 30

def test_solar_inverter_to_pvlib(sample_inverter):
    d = sample_inverter.to_pvlib_dict()
    assert d['pdc0'] == 5000
    assert d['eta_inv_nom'] == 0.96

def test_parse_location():
    loc_req = SimpleNamespace(latitude=52.2, longitude=21.0, tz='UTC', altitude=100)
    loc = parse_location(loc_req)
    assert loc.latitude == 52.2
    assert loc.longitude == 21.0
    assert loc.tz == 'UTC'

def test_solar_array_scaling(sample_panel):
    array_single = SolarArray(sample_panel, 1, 1, 30, 180)
    array_multi = SolarArray(sample_panel, 10, 2, 30, 180)
    
    pv_single = array_single.to_pvlib_array()
    pv_multi = array_multi.to_pvlib_array()
    
    assert pv_single.modules_per_string == 1
    assert pv_single.strings == 1
    assert pv_multi.modules_per_string == 10
    assert pv_multi.strings == 2

def test_solve_basic(sample_panel, sample_inverter):
    from pvlib.location import Location
    loc = Location(52.2, 21.0, 'UTC', 100)
    weather = pd.DataFrame({
        'ghi': [1000, 0],
        'dni': [800, 0],
        'dhi': [200, 0],
        'temp_air': [25, 25],
        'wind_speed': [2, 2]
    }, index=pd.to_datetime(['2026-06-21 12:00:00', '2026-06-21 23:00:00']).tz_localize('UTC'))
    
    array = SolarArray(sample_panel, 10, 2, 30, 180)
    results = solve([array], sample_inverter, loc, weather)
    
    assert len(results) == 2
    assert results.iloc[0] > 0
    assert results.iloc[1] == 0  # Night

def test_solve_east_west(sample_panel, sample_inverter):
    from pvlib.location import Location
    loc = Location(52.2, 21.0, 'UTC', 100)
    weather = pd.DataFrame({
        'ghi': [1000], 'dni': [800], 'dhi': [200], 'temp_air': [25], 'wind_speed': [2]
    }, index=pd.to_datetime(['2026-06-21 12:00:00']).tz_localize('UTC'))
    
    # One array facing East (90), one facing West (270)
    east_array = SolarArray(sample_panel, 10, 1, 30, 90)
    west_array = SolarArray(sample_panel, 10, 1, 30, 270)
    
    results = solve([east_array, west_array], sample_inverter, loc, weather)
    
    assert len(results) == 1
    assert results.iloc[0] > 0
    
    # Verify that a combined system produces more than a single orientation (if sun is high)
    res_east = solve([east_array], sample_inverter, loc, weather)
    assert results.iloc[0] > res_east.iloc[0]
