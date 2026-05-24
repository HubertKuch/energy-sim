import pandas as pd
import numpy as np
from pvlib.modelchain import ModelChain
from .battery import SolarBattery
from .inverter import SolarInverter
from .array import SolarArray
from .location import Location
from .context import SimulationContext
from ..modifiers.group import ModifierGroup
from ..modifiers.snow import SnowModifier
from ..modifiers.temperature import TemperatureModifier
from ..modifiers.wind import WindModifier
from ..modifiers.orientation import OrientationModifier

class SolarSystem:
    def __init__(self, arrays: list[SolarArray], inverter: SolarInverter, battery: SolarBattery = None):
        self.arrays = arrays
        self.inverter = inverter
        self.battery = battery
        
        # Default modifiers
        self.modifiers = ModifierGroup([
            OrientationModifier(),
            TemperatureModifier(),
            WindModifier(),
            SnowModifier()
        ])

    def simulate(self, location: Location, weather_df: pd.DataFrame, load_profile: list[float] = None):
        total_ac_kw = pd.Series(0.0, index=weather_df.index)
        
        for array in self.arrays:
            total_ac_kw += self._simulate_array(array, location, weather_df)

        load_profile = self._prepare_load_profile(load_profile, len(total_ac_kw))
        
        return self._process_battery_and_grid(total_ac_kw, load_profile)

    def _simulate_array(self, array: SolarArray, location: Location, weather_df: pd.DataFrame) -> pd.Series:
        from pvlib.pvsystem import PVSystem as LibPVSystem
        temp_sys = LibPVSystem(
            arrays=[array.to_pvlib_array()],
            inverter_parameters=self.inverter.to_pvlib_dict()
        )
        mc = ModelChain(
            temp_sys, 
            location, 
            spectral_model='no_loss', 
            aoi_model='no_loss',
            ac_model='pvwatts'
        )
        mc.run_model(weather_df)
        
        raw_dc = mc.results.dc
        if isinstance(raw_dc, pd.DataFrame):
            raw_dc = raw_dc.sum(axis=1)

        array_ac_kw = []
        for i in range(len(weather_df)):
            ctx = SimulationContext(
                weather=weather_df.iloc[i],
                array=array,
                location=location,
                raw_dc_power=raw_dc.iloc[i],
                dc_power=raw_dc.iloc[i],
                loss_factors={}
            )
            ctx = self.modifiers.apply(ctx)
            ac_w = self.inverter.calculate_ac(ctx.dc_power)
            array_ac_kw.append(ac_w / 1000.0)
        
        return pd.Series(array_ac_kw, index=weather_df.index)

    def _prepare_load_profile(self, load_profile: list[float], length: int) -> list[float]:
        if not load_profile:
            return [0.0] * length
        if len(load_profile) < length:
            return load_profile + [load_profile[-1]] * (length - len(load_profile))
        return load_profile[:length]

    def _process_battery_and_grid(self, total_ac_kw: pd.Series, load_profile: list[float]):
        battery_soc = []
        grid_import = []
        grid_export = []
        
        for ac, load in zip(total_ac_kw, load_profile):
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
                
        return total_ac_kw * 1000.0, battery_soc, grid_import, grid_export
