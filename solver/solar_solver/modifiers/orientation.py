from .base import Modifier
from ..domain.context import SimulationContext

class OrientationModifier(Modifier):
    def apply(self, context: SimulationContext) -> SimulationContext:
        """
        Records the orientation (Tilt/Azimuth) context.
        """
        context.loss_factors['tilt'] = context.array.tilt
        context.loss_factors['azimuth'] = context.array.azimuth
        return context
