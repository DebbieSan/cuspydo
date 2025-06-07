import pytest
from weather import getCleanGeoCodeInfo, Coordinates

bonnResponse = """{"results":[{"id":2946447,"name":"Bonn","latitude":50.73438,"longitude":7.09549,"elevation":64.0,"feature_code":"PPLA3","country_code":"DE","admin1_id":2861876,"admin2_id":2886241,"admin3_id":3247450,"admin4_id":6553048,"timezone":"Europe/Berlin","population":330579,"country_id":2921044,"country":"Germany","admin1":"North Rhine-Westphalia","admin2":"Cologne District","admin3":"Kreisfreie Stadt Bonn","admin4":"Bonn"}],"generationtime_ms":0.78070164}"""        


@pytest.mark.asyncio
async def test_getCleanGeoCodeInfo():
    coordinates = Coordinates(lat=50.73438, long=7.09549)
    result = await getCleanGeoCodeInfo(bonnResponse)
    assert result == coordinates

