import requests
from typing import Tuple, Optional, Dict
from django.conf import settings

class GeoCodeService:
    """Service for converting a location name to its end co-ordinates"""

    def __init__(self):
        self.api_key = settings.ORS_API_KEY
        self.base_url = "https://api.openrouteservice.org"
    
    def geocode(self, location: str) -> Optional[Tuple[float, float]]:
        url = "https://api.openrouteservice.org/geocode/search"
        params = {
            "api_key" : settings.ORS_API_KEY,
            "text" : location,
            'boundary.country': 'US', #Inside US only for the asssignment purpose
            'size': 1
        }
        print(params)
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data['features']:
                coords = data['features'][0]['geometry']['coordinates']
                return (coords[1], coords[0])  # Return as (lat, lon)
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"Geocoding error: {e}")
            return None

      