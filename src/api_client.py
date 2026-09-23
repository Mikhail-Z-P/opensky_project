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
            "latitude": float(data[0]["lat"]),
            "longitude": float(data[0]["lon"]),
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
        return data.get("states", [])

    @staticmethod
    def parse_state_vector(state: List[Any]) -> Dict[str, Any]:
        """Преобразует state vector (массив) в словарь."""
        return {
            "icao24": state[0],
            "callsign": state[1],
            "origin_country": state[2],
            "longitude": state[5],
            "latitude": state[6],
            "baro_altitude": state[7],
            "on_ground": state[8],
            "velocity": state[9],
            "true_track": state[10],
            "vertical_rate": state[11],
            "geo_altitude": state[13],
            "squawk": state[14],
        }
