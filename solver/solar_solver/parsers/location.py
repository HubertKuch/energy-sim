from pvlib.location import Location

def parse_location(request_location) -> Location:
    return Location(
        latitude=request_location.latitude,
        longitude=request_location.longitude,
        tz=request_location.tz,
        altitude=request_location.altitude
    )
