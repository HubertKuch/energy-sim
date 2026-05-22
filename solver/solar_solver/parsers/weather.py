import pandas as pd

def parse_weather_data(weather_list, tz: str) -> pd.DataFrame:
    weather_df = pd.DataFrame([
        {
            'timestamp': w.timestamp, 'ghi': w.ghi, 'dni': w.dni, 'dhi': w.dhi, 'temp_air': w.temp_air, 'wind_speed': w.wind_speed
        } for w in weather_list
    ])
    weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
    weather_df.set_index('timestamp', inplace=True)
    if weather_df.index.tz is None:
        weather_df.index = weather_df.index.tz_localize(tz)
    return weather_df
