from abc import ABC, abstractmethod
from ..domain.context import SimulationContext

class Modifier(ABC):
    @abstractmethod
    def apply(self, context: SimulationContext) -> SimulationContext:
        """
        Takes a context, modifies its state, and returns it.
        """
        pass
