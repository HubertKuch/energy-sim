from .base import Modifier
from ..domain.context import SimulationContext

class ModifierGroup(Modifier):
    def __init__(self, modifiers: list[Modifier] = None):
        self.modifiers = modifiers or []

    def add(self, modifier: Modifier):
        self.modifiers.append(modifier)

    def apply(self, context: SimulationContext) -> SimulationContext:
        for modifier in self.modifiers:
            context = modifier.apply(context)
        return context
