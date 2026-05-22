import pandas as pd
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from .battery import SolarBattery
from .inverter import SolarInverter
from .array import SolarArray

class SolarSystem:
    def __init__(self, arrays: list[SolarArray], inverter: SolarInverter, battery: SolarBattery = None):
        self.arrays = arrays
        self.inverter = inverter
        self.battery = battery

    def simulate(self, location: Location, weather_df: pd.DataFrame, load_profile: list[float] = None):
        pv_system = PVSystem(
            arrays=[a.to_pvlib_array() for a in self.arrays],
            inverter_parameters=self.inverter.to_pvlib_dict()
        )
        
        mc = ModelChain(pv_system, location, spectral_model='no_loss', aoi_model='no_loss')
        mc.run_model(weather_df)

        ac_output_w = mc.results.ac
        ac_output_kw = ac_output_w / 1000.0
        
        if not load_profile:
            load_profile = [0.0] * len(ac_output_kw)
        elif len(load_profile) < len(ac_output_kw):
            load_profile.extend([load_profile[-1]] * (len(ac_output_kw) - len(load_profile)))
        
        battery_soc = []
        grid_import = []
        grid_export = []
        
        for ac, load in zip(ac_output_kw, load_profile):
            net_power = ac - load
            
            if self.battery:
                battery_power = self.battery.step(net_power)
                net_after_battery = net_power - battery_power
                battery_soc.append(self.battery.current_soc_kwh)
            else:
                net_after_battery = net_power
                battery_soc.append(0.0)
                
            if net_after_battery > 0:
                grid_export.append(net_after_battery)
                grid_import.append(0.0)
            else:
                grid_import.append(abs(net_after_battery))
                grid_export.append(0.0)
                
        return ac_output_w, battery_soc, grid_import, grid_export
