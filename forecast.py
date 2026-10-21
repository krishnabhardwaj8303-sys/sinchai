import requests

def get_forecast(lat=21.25, lon=81.63):
    """Open-Meteo (free, bina key). Fail ho to None."""
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat, "longitude": lon, "forecast_days": 3, "timezone": "auto",
            "daily": "precipitation_sum,temperature_2m_min,temperature_2m_max"}, timeout=8)
        r.raise_for_status()
        j = r.json()["daily"]
        daily = [float(x or 0) for x in j["precipitation_sum"]]
        return {"rain3": sum(daily), "daily": daily,
                "tmin": float(min(j["temperature_2m_min"])),
                "tmax": float(max(j["temperature_2m_max"]))}
    except Exception:
        return None