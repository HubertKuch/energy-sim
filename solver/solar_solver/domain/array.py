from pvlib.pvsystem import Array, FixedMount
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from .panel import SolarPanel

class SolarArray:
    def __init__(self, panel: SolarPanel, modules_per_string: int, strings: int, tilt: float, azimuth: float):
        self.panel = panel
        self.modules_per_string = modules_per_string
        self.strings = strings
        self.tilt = tilt
        self.azimuth = azimuth

    def to_pvlib_array(self):
        temp_params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
        mount = FixedMount(surface_tilt=self.tilt, surface_azimuth=self.azimuth)
        return Array(
            mount=mount,
            module_parameters=self.panel.to_pvlib_dict(),
            temperature_model_parameters=temp_params,
            modules_per_string=self.modules_per_string,
            strings=self.strings
        )
