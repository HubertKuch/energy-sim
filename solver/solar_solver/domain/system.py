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
        # We need to calculate DC power per array to apply modifiers per array
        total_ac_kw = pd.Series(0.0, index=weather_df.index)
        
        # Inverter efficiency (simple for now, as we focus on DC modifiers)
        inv_eta = self.inverter.eta_inv_nom

        for array in self.arrays:
            # 1. Get raw DC power from pvlib for this specific array
            from pvlib.pvsystem import PVSystem as LibPVSystem
            temp_sys = LibPVSystem(
                arrays=[array.to_pvlib_array()],
                inverter_parameters=self.inverter.to_pvlib_dict()
            )
            # Use fixed efficiency AC model to avoid parameter inference issues
            mc = ModelChain(
                temp_sys, 
                location, 
                spectral_model='no_loss', 
                aoi_model='no_loss',
                ac_model='pvwatts'
            )
            mc.run_model(weather_df)
            
            # Use total DC power (sum of all arrays in temp_sys, which is just one)
            raw_dc = mc.results.dc
            if isinstance(raw_dc, pd.DataFrame):
                # If multiple arrays were present, mc.results.dc would be a DF.
                # Here we have one array, but pvlib might return a DF with one column.
                raw_dc = raw_dc.sum(axis=1)

            array_ac_kw = []
            
            # 2. Apply modifiers per timestamp
            for i in range(len(weather_df)):
                ctx = SimulationContext(
                    weather=weather_df.iloc[i],
                    array=array,
                    location=location,
                    raw_dc_power=raw_dc.iloc[i],
                    dc_power=raw_dc.iloc[i],
                    loss_factors={}
                )
                
                # Apply modifier pipeline
                ctx = self.modifiers.apply(ctx)
                
                # Convert DC to AC (kW)
                ac_kw = (ctx.dc_power * inv_eta) / 1000.0
                array_ac_kw.append(ac_kw)
            
            total_ac_kw += pd.Series(array_ac_kw, index=weather_df.index)

        # 3. Handle Battery and Load Profile (System level)
        if not load_profile:
            load_profile = [0.0] * len(total_ac_kw)
        elif len(load_profile) < len(total_ac_kw):
            load_profile.extend([load_profile[-1]] * (len(total_ac_kw) - len(load_profile)))
        
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
