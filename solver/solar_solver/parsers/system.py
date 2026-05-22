from ..domain.panel import SolarPanel
from ..domain.array import SolarArray
from ..domain.inverter import SolarInverter
from ..domain.battery import SolarBattery
from ..domain.system import SolarSystem

def parse_system(system_config) -> SolarSystem:
    arrays = []
    for arr_config in system_config.arrays:
        panel = SolarPanel(
            pdc0=arr_config.panel.pdc0, v_mp=arr_config.panel.v_mp, i_mp=arr_config.panel.i_mp,
            v_oc=arr_config.panel.v_oc, i_sc=arr_config.panel.i_sc, gamma_pdc=arr_config.panel.gamma_pdc,
            alpha_sc=arr_config.panel.alpha_sc, beta_voc=arr_config.panel.beta_voc, cells_in_series=arr_config.panel.cells_in_series
        )
        arrays.append(SolarArray(panel, arr_config.modules_per_string, arr_config.strings, arr_config.surface_tilt, arr_config.surface_azimuth))
    
    inverter = SolarInverter(system_config.inverter.pdc0, system_config.inverter.eta_inv_nom, system_config.inverter.v_dc_max)
    
    battery = None
    if system_config.HasField('battery'):
        b = system_config.battery
        battery = SolarBattery(b.capacity_kwh, b.max_charge_kw, b.max_discharge_kw, b.efficiency, b.initial_soc_kwh)
        
    return SolarSystem(arrays, inverter, battery)
