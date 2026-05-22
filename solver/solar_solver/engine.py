import pandas as pd
from pvlib.location import Location
from .domain.panel import SolarPanel
from .domain.inverter import SolarInverter
from .domain.battery import SolarBattery
from .domain.array import SolarArray
from .domain.system import SolarSystem
from .parsers.location import parse_location
from .parsers.system import parse_system
from .parsers.weather import parse_weather_data

def solve_solar(request):
    """
    gRPC entry point.
    """
    location = parse_location(request.location)
    system = parse_system(request.system_config)
    weather_df = parse_weather_data(request.weather, location.tz)
    
    ac_output, battery_soc, grid_import, grid_export = system.simulate(location, weather_df, list(request.load_profile_kw))
    
    from solar_solver.pb import solar_pb2
    return solar_pb2.SolarResponse(
        ac_output=ac_output.tolist(),
        timestamps=[str(ts) for ts in ac_output.index],
        battery_soc_kwh=battery_soc,
        grid_import_kw=grid_import,
        grid_export_kw=grid_export
    )

def solve(arrays: list[SolarArray], inverter: SolarInverter, location: Location, weather_df: pd.DataFrame, battery: SolarBattery = None, load_profile: list[float] = None):
    """
    Domain entry point.
    """
    system = SolarSystem(arrays, inverter, battery)
    ac_output, battery_soc, grid_import, grid_export = system.simulate(location, weather_df, load_profile)
    return ac_output
