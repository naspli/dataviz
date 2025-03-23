import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


def get_city_info(city_name: str):
    # Initialize the geocoder with a unique user agent
    geolocator = Nominatim(user_agent="city_locator")
    location = geolocator.geocode(city_name)
    if location is None:
        raise ValueError(f"Could not find city: {city_name}")

    # Retrieve latitude and longitude
    lat = location.latitude
    lon = location.longitude

    # Find the timezone using the coordinates
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    if timezone_str is None:
        raise ValueError("Could not determine timezone for the given location.")

    return lat, lon, pytz.timezone(timezone_str)