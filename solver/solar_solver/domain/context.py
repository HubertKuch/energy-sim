from dataclasses import dataclass
import pandas as pd
from ..domain.array import SolarArray
from ..domain.location import Location

@dataclass
class SimulationContext:
    """
    Context passed through modifiers.
    
    Attributes:
        weather: Row of weather data for the current timestamp.
        array: The specific SolarArray being simulated.
        location: GPS and altitude data.
        raw_dc_power: Initial DC power from pvlib before modifiers.
        dc_power: Adjusted DC power after modifiers.
        loss_factors: Dictionary tracking loss/gain from each modifier for auditing.
    """
    weather: pd.Series
    array: SolarArray
    location: Location
    raw_dc_power: float
    dc_power: float
    loss_factors: dict[str, float]
