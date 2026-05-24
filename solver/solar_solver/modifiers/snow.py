from .base import Modifier
from ..domain.context import SimulationContext
from ..domain.snow import SnowModel

class SnowModifier(Modifier):
    def apply(self, context: SimulationContext) -> SimulationContext:
        snow_coverage = SnowModel.calculate_coverage_fraction(
            snow_depth=context.weather.get('snow_depth', 0),
            tilt=context.array.tilt,
            temp_air=context.weather.temp_air,
            ghi=context.weather.ghi
        )
        
        # Apply loss
        multiplier = 1.0 - snow_coverage
        context.dc_power *= multiplier
        context.loss_factors['snow'] = snow_coverage
        
        return context
