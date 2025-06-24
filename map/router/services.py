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

class RouteService:
    """Service for gettingroute given start and end point"""     

    def __init__(self):
        self.api_key = settings.ORS_API_KEY
        self.base_url = "https://api.openrouteservice.org"

    def get_route(self, start_coords, end_coords):
        url = f"{self.base_url}/v2/directions/driving-car"

        # ORS expects coordinates as [longitude, latitude]
        coordinates = [
            [start_coords[1], start_coords[0]],  # start: [lon, lat]
            [end_coords[1], end_coords[0]]       # end: [lon, lat]
        ]

        payload = {
            'coordinates': coordinates,
            'format': 'json',
            'instructions': True,
            'geometry': True,
            'elevation': False
        }

        headers = {
            'Accept': 'application/json',
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Routing error: {e}")
            return None
