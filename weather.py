import aiohttp  
import asyncio    
import json

from dataclasses import dataclass

@dataclass
class Coordinates:
    lat:float
    long:float


async def getRawWeatherInfo(lat:str, long:str) -> str:
    async with aiohttp.ClientSession() as session:
        weatherurl = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current=temperature_2m"
        async with session.get(weatherurl) as resp:
            # to do handle response status (resp.status)
            print(await resp.text())
            return await resp.text()


async def getRawGeoCodeInfo(city:str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json") as resp:
            # to do handle response status (resp.status)
            return await resp.text()
        

async def getCleanGeoCodeInfo(city:str) -> Coordinates:
    respDict = json.loads(city)
    result = respDict["results"][0]
    lat = result["latitude"]
    long = result["longitude"]
    return Coordinates(lat, long)

async def getCleanWeatherInfo(city:str) -> Coordinates:
    respDict = json.loads(city)
    return respDict["current"]["temperature_2m"]

asyncio.run(getRawWeatherInfo("50.73438","7.09549"))

