import time
import requests
from typing import List, Dict, Any, Optional


class NominatimClient:
    """Клиент для получения координат стран через Nominatim API."""

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    @staticmethod
    def get_country_coordinates(country_name: str) -> Optional[Dict[str, float]]:
        """Возвращает широту и долготу страны."""
        headers = {"User-Agent": "opensky_project/1.0"}
        params = {"country": country_name, "format": "json", "limit": 1}
        response = requests.get(NominatimClient.BASE_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        return {
            "latitude": float(data["lat"]),
            "longitude": float(data["lon"])
        }


class OpenSkyClient:
    """Клиент для получения данных о самолётах через OpenSky API."""

    BASE_URL = "https://opensky-network.org/api/states/all"

    @staticmethod
    def get_all_states() -> List[List[Any]]:
        """Возвращает все state vectors самолётов."""
        response = requests.get(OpenSkyClient.BASE_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("states", )

    @staticmethod
    def parse_state_vector(state: List[Any]) -> Dict[str, Any]:
        """Преобразует state vector (массив) в словарь."""
        return {
            "icao24": state,
            "callsign": state,
        "origin_country": state,
        "longitude": state,
        "latitude": state,
        "baro_altitude": state,
        "on_ground": state,
        "velocity": state,
        "true_track": state,
        "vertical_rate": state,
        "geo_altitude": state,
        "squawk": state
        }
