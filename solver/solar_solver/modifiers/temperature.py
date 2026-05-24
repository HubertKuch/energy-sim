from .base import Modifier
from ..domain.context import SimulationContext

class TemperatureModifier(Modifier):
    def apply(self, context: SimulationContext) -> SimulationContext:
        """
        Applies temperature-related DC power derating.
        
        Note: pvlib already calculates DC power including temperature effects 
        if parameters are provided to ModelChain. This modifier serves as a 
        placeholder for custom/advanced temperature logic (e.g. thermal mass, 
        specific local hotspots).
        
        For now, it records the ambient temperature in loss_factors.
        """
        context.loss_factors['ambient_temp'] = context.weather.temp_air
        return context
