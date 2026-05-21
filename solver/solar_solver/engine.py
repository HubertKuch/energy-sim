import pandas as pd
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem, Array, FixedMount
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

class SolarPanel:
    def __init__(self, pdc0, v_mp, i_mp, v_oc, i_sc, gamma_pdc, alpha_sc, beta_voc, cells_in_series):
        self.pdc0 = pdc0
        self.v_mp = v_mp
        self.i_mp = i_mp
        self.v_oc = v_oc
        self.i_sc = i_sc
        self.gamma_pdc = gamma_pdc
        self.alpha_sc = alpha_sc
        self.beta_voc = beta_voc
        self.cells_in_series = cells_in_series

    def to_pvlib_dict(self):
        return {
            'pdc0': self.pdc0,
            'v_mp': self.v_mp,
            'i_mp': self.i_mp,
            'v_oc': self.v_oc,
            'i_sc': self.i_sc,
            'gamma_pdc': self.gamma_pdc,
            'alpha_sc': self.alpha_sc,
            'beta_voc': self.beta_voc,
            'cells_in_series': self.cells_in_series,
        }

class SolarInverter:
    def __init__(self, pdc0, eta_inv_nom, v_dc_max):
        self.pdc0 = pdc0
        self.eta_inv_nom = eta_inv_nom
        self.v_dc_max = v_dc_max

    def to_pvlib_dict(self):
        return {
            'pdc0': self.pdc0,
            'eta_inv_nom': self.eta_inv_nom,
            'v_dc_max': self.v_dc_max,
        }

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

def parse_location(request_location) -> Location:
    return Location(
        latitude=request_location.latitude,
        longitude=request_location.longitude,
        tz=request_location.tz,
        altitude=request_location.altitude
    )

def parse_arrays(system_config) -> list[Array]:
    arrays = []
    for arr_config in system_config.arrays:
        panel = SolarPanel(
            pdc0=arr_config.panel.pdc0,
            v_mp=arr_config.panel.v_mp,
            i_mp=arr_config.panel.i_mp,
            v_oc=arr_config.panel.v_oc,
            i_sc=arr_config.panel.i_sc,
            gamma_pdc=arr_config.panel.gamma_pdc,
            alpha_sc=arr_config.panel.alpha_sc,
            beta_voc=arr_config.panel.beta_voc,
            cells_in_series=arr_config.panel.cells_in_series
        )
        
        solar_array = SolarArray(
            panel=panel,
            modules_per_string=arr_config.modules_per_string,
            strings=arr_config.strings,
            tilt=arr_config.surface_tilt,
            azimuth=arr_config.surface_azimuth
        )
        arrays.append(solar_array.to_pvlib_array())
        
    return arrays

def parse_inverter(inverter_config) -> SolarInverter:
    return SolarInverter(
        pdc0=inverter_config.pdc0,
        eta_inv_nom=inverter_config.eta_inv_nom,
        v_dc_max=inverter_config.v_dc_max,
    )

def create_pv_system(system_config) -> PVSystem:
    arrays = parse_arrays(system_config)
    if not arrays:
        raise ValueError("SystemConfig must contain at least one SolarArray")

    inverter = parse_inverter(system_config.inverter)
    return PVSystem(arrays=arrays, inverter_parameters=inverter.to_pvlib_dict())

def parse_weather_data(weather_list, tz: str) -> pd.DataFrame:
    weather_df = pd.DataFrame([
        {
            'timestamp': w.timestamp,
            'ghi': w.ghi,
            'dni': w.dni,
            'dhi': w.dhi,
            'temp_air': w.temp_air,
            'wind_speed': w.wind_speed
        } for w in weather_list
    ])
    
    weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
    weather_df.set_index('timestamp', inplace=True)
    
    if weather_df.index.tz is None:
        weather_df.index = weather_df.index.tz_localize(tz)
        
    return weather_df

def solve_solar(request):
    """
    gRPC entry point.
    """
    location = parse_location(request.location)
    system = create_pv_system(request.system_config)
    weather_df = parse_weather_data(request.weather, location.tz)

    mc = ModelChain(system, location, spectral_model='no_loss', aoi_model='no_loss')
    mc.run_model(weather_df)

    return mc.results.ac

def solve(panel: SolarPanel, inverter: SolarInverter, modules_per_string: int, strings: int, location: Location, weather_df: pd.DataFrame):
    """
    Domain-specific solve function.
    """
    solar_array = SolarArray(
        panel=panel,
        modules_per_string=modules_per_string,
        strings=strings,
        tilt=30,
        azimuth=180
    )
    
    system = PVSystem(
        arrays=[solar_array.to_pvlib_array()],
        inverter_parameters=inverter.to_pvlib_dict()
    )
    
    mc = ModelChain(system, location, spectral_model='no_loss', aoi_model='no_loss')
    mc.run_model(weather_df)
    return mc.results.ac
