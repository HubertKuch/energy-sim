import pandas as pd
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem, Array, FixedMount
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

def solve_solar(request):
    """
    Core logic to run the pvlib ModelChain based on the gRPC request.
    """
    location = Location(
        latitude=request.location.latitude,
        longitude=request.location.longitude,
        tz=request.location.tz,
        altitude=request.location.altitude
    )

    module_parameters = {
        'pdc0': request.system_config.module_parameters.pdc0,
        'gamma_pdc': request.system_config.module_parameters.gamma_pdc
    }
    
    inverter_parameters = {
        'pdc0': request.system_config.inverter_parameters.pdc0,
        'eta_inv_nom': request.system_config.inverter_parameters.eta_inv_nom
    }
    
    temp_params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

    mount = FixedMount(
        surface_tilt=request.system_config.surface_tilt,
        surface_azimuth=request.system_config.surface_azimuth
    )
    
    array = Array(
        mount=mount, 
        module_parameters=module_parameters,
        temperature_model_parameters=temp_params
    )
    
    system = PVSystem(arrays=[array], inverter_parameters=inverter_parameters)

    # Use standard models for simplicity and speed
    mc = ModelChain(system, location, spectral_model='no_loss', aoi_model='no_loss')

    weather_df = pd.DataFrame([
        {
            'timestamp': w.timestamp,
            'ghi': w.ghi,
            'dni': w.dni,
            'dhi': w.dhi,
            'temp_air': w.temp_air,
            'wind_speed': w.wind_speed
        } for w in request.weather
    ])
    
    weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
    weather_df.set_index('timestamp', inplace=True)
    
    if weather_df.index.tz is None:
        weather_df.index = weather_df.index.tz_localize(location.tz)

    mc.run_model(weather_df)

    return mc.results.ac
