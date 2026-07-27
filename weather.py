import aiohttp
import json

from dataclasses import dataclass


@dataclass
class Coordinates:
    lat: float
    long: float


# Open-Meteo returns weather conditions as numeric WMO codes.
WEATHER_CODE_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Freezing fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Heavy drizzle",
    56: "Light freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Heavy rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with light hail",
    99: "Thunderstorm with heavy hail"
}


async def getRawWeatherInfo(
    lat: float,
    long: float,
    unit: str = "c"
) -> str:
    """
    Request current weather information from Open-Meteo.

    unit:
        "c" returns Celsius, km/h, and millimetres.
        "f" returns Fahrenheit, mph, and inches.
    """

    unit = unit.lower()
    use_fahrenheit = unit in ("f", "fahrenheit")

    # These parameters are safely added to the URL by aiohttp.
    params = {
        "latitude": lat,
        "longitude": long,

        # Ask the API for all the current weather fields needed.
        "current": (
            "temperature_2m,"
            "apparent_temperature,"
            "relative_humidity_2m,"
            "precipitation,"
            "weather_code,"
            "cloud_cover,"
            "pressure_msl,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "wind_gusts_10m"
        ),

        # Let Open-Meteo perform the unit conversions.
        "temperature_unit": (
            "fahrenheit" if use_fahrenheit else "celsius"
        ),
        "wind_speed_unit": (
            "mph" if use_fahrenheit else "kmh"
        ),
        "precipitation_unit": (
            "inch" if use_fahrenheit else "mm"
        ),

        # Return weather times using the location's time zone.
        "timezone": "auto"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.open-meteo.com/v1/forecast",
            params=params
        ) as resp:
            response_text = await resp.text()

            # Raise an error if the API request failed.
            if resp.status != 200:
                raise RuntimeError(
                    f"Weather API returned status {resp.status}: "
                    f"{response_text}"
                )

            return response_text


async def getRawGeoCodeInfo(city: str) -> str:
    """
    Search for the latitude and longitude of a city.
    """

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params=params
        ) as resp:
            response_text = await resp.text()

            if resp.status != 200:
                raise RuntimeError(
                    f"Geocoding API returned status {resp.status}: "
                    f"{response_text}"
                )

            return response_text


async def getCleanGeoCodeInfo(city: str) -> Coordinates:
    """
    Convert the geocoding JSON response into Coordinates.
    """

    response_dict = json.loads(city)

    # Use .get() because some searches may not return results.
    results = response_dict.get("results")

    if not results:
        raise ValueError("I couldn't find that location.")

    first_result = results[0]

    return Coordinates(
        lat=first_result["latitude"],
        long=first_result["longitude"]
    )


def degreesToCompass(degrees: float) -> str:
    """
    Convert a wind direction such as 225 degrees into SW.
    """

    directions = [
        "N",
        "NE",
        "E",
        "SE",
        "S",
        "SW",
        "W",
        "NW"
    ]

    index = round(degrees / 45) % 8

    return directions[index]


async def getCleanWeatherInfo(
    weather_data: str,
    location: str,
    unit: str = "c",
    features=None
) -> str:
    """
    Convert the weather JSON response into a Discord message.

    Available features:
        summary
        conditions
        temperature
        feels
        humidity
        wind
        rain
        clouds
        pressure
        all
    """

    if features is None:
        features = ["summary"]

    response_dict = json.loads(weather_data)

    current = response_dict.get("current")
    current_units = response_dict.get("current_units", {})

    if not current:
        raise ValueError(
            "The weather service did not return current conditions."
        )

    # Convert the list into a set to prevent repeated features.
    selected_features = set(features)

    # "all" displays every available feature.
    if "all" in selected_features:
        selected_features = {
            "conditions",
            "temperature",
            "feels",
            "humidity",
            "wind",
            "rain",
            "clouds",
            "pressure"
        }

    # The default summary includes these three features.
    elif "summary" in selected_features:
        selected_features.update({
            "conditions",
            "temperature",
            "feels"
        })

    # Get the actual units returned by Open-Meteo.
    temperature_unit = current_units.get(
        "temperature_2m",
        "°F" if unit == "f" else "°C"
    )

    wind_unit = current_units.get(
        "wind_speed_10m",
        "mph" if unit == "f" else "km/h"
    )

    precipitation_unit = current_units.get(
        "precipitation",
        "in" if unit == "f" else "mm"
    )

    pressure_unit = current_units.get(
        "pressure_msl",
        "hPa"
    )

    # Start building the Discord message.
    lines = [
        f"🌤️ **Weather for {location.title()}**"
    ]

    if "conditions" in selected_features:
        weather_code = current.get("weather_code")

        description = WEATHER_CODE_DESCRIPTIONS.get(
            weather_code,
            "Unknown conditions"
        )

        lines.append(
            f"**Conditions:** {description}"
        )

    if "temperature" in selected_features:
        temperature = current.get("temperature_2m")

        if temperature is not None:
            lines.append(
                f"**Temperature:** "
                f"{temperature:.1f}{temperature_unit}"
            )

    if "feels" in selected_features:
        feels_like = current.get("apparent_temperature")

        if feels_like is not None:
            lines.append(
                f"**Feels like:** "
                f"{feels_like:.1f}{temperature_unit}"
            )

    if "humidity" in selected_features:
        humidity = current.get("relative_humidity_2m")

        if humidity is not None:
            lines.append(
                f"**Humidity:** {humidity}%"
            )

    if "wind" in selected_features:
        wind_speed = current.get("wind_speed_10m")
        wind_gusts = current.get("wind_gusts_10m")
        wind_degrees = current.get("wind_direction_10m")

        if wind_speed is not None:
            wind_text = f"{wind_speed:.1f} {wind_unit}"

            if wind_degrees is not None:
                direction = degreesToCompass(wind_degrees)

                wind_text += (
                    f" from {direction} "
                    f"({wind_degrees:.0f}°)"
                )

            if wind_gusts is not None:
                wind_text += (
                    f", gusting to "
                    f"{wind_gusts:.1f} {wind_unit}"
                )

            lines.append(
                f"**Wind:** {wind_text}"
            )

    if "rain" in selected_features:
        precipitation = current.get("precipitation")

        if precipitation is not None:
            lines.append(
                f"**Precipitation:** "
                f"{precipitation:.2f} "
                f"{precipitation_unit}"
            )

    if "clouds" in selected_features:
        cloud_cover = current.get("cloud_cover")

        if cloud_cover is not None:
            lines.append(
                f"**Cloud cover:** {cloud_cover}%"
            )

    if "pressure" in selected_features:
        pressure = current.get("pressure_msl")

        if pressure is not None:
            lines.append(
                f"**Pressure:** "
                f"{pressure:.1f} {pressure_unit}"
            )

    return "\n".join(lines)
