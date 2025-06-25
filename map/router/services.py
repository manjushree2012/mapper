import requests
from typing import Tuple, Optional, Dict
from django.conf import settings
from django.core.cache import cache
import hashlib
import json

class GeoCodeService:
    """Service for converting a location name to its end co-ordinates"""

    def __init__(self):
        self.api_key = settings.ORS_API_KEY
        self.base_url = "https://api.openrouteservice.org"
    
    def _cache_key(self, location: str) -> str:
        # Normalize and hash to prevent Redis key issues
        normalized = location.strip().lower()
        return "geocode:" + hashlib.md5(normalized.encode()).hexdigest()

    def geocode(self, location: str) -> Optional[Tuple[float, float]]:
        # Try to get coordinates from cache first
        key = self._cache_key(location)
        cached_value = cache.get(key)
        if cached_value:
            return tuple(json.loads(cached_value))

        # If not in cache, make API call
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
                result = (coords[1], coords[0])  # Convert to (lat, lon)
                # Store in cache for 30 days (in seconds)
                cache.set(key, json.dumps(result), timeout=30 * 24 * 60 * 60)
                return result
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


import csv
from typing import List, Tuple, Optional
from geopy.distance import geodesic
from dataclasses import dataclass

@dataclass
class FuelStation:
    name: str
    latitude: float
    longitude: float
    fuel_price: float

from shapely.geometry import Point

class FuelPlannerService:
    def __init__(self,
                 csv_path: str,
                 fuel_range_miles: float = 500,
                 mpg: float = 10,
                 route_polygon=None
                 ):
        self.csv_path = csv_path
        self.fuel_range_miles = fuel_range_miles
        self.mpg = mpg
        self.route_polygon = route_polygon

        self.stations = self._load_stations()

    def _load_stations(self) -> List[FuelStation]:
        stations = []
        with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    #Now that CSVfile contains co-ordinates, I will directly calculate from here
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])

                    # If polygon provided, filter by whether it's inside it
                    if self.route_polygon:
                        point = Point(lon, lat)
                        if not self.route_polygon.contains(point):
                            continue

                    station = FuelStation(
                        name=row['Truckstop Name'],
                        latitude=lat,
                        longitude=lon,
                        fuel_price=float(row['Retail Price'])
                    )
                    stations.append(station)

                except Exception:
                    continue  # Ignore bad rows

        return stations

    def _find_best_station_near_point(
        self, point: Tuple[float, float], max_distance_miles: float = 25
    ) -> Optional[FuelStation]:
        lat, lon = point
        degree_buffer = max_distance_miles / 69.0  # Rough approximation

        nearby_stations = [
            s for s in self.stations
            if (lat - degree_buffer <= s.latitude <= lat + degree_buffer) and
               (lon - degree_buffer <= s.longitude <= lon + degree_buffer)
        ]

        # Filter by real distance and select cheapest
        filtered = []
        for s in nearby_stations:
            dist = geodesic(point, (s.latitude, s.longitude)).miles
            if dist <= max_distance_miles:
                filtered.append(s)

        if filtered:
            return sorted(filtered, key=lambda s: s.fuel_price)[0]
        return None

    def _get_fuel_stop_points(self, route_coords: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        stops = []
        distance = 0
        for i in range(1, len(route_coords)):
            segment = geodesic(route_coords[i - 1], route_coords[i]).miles
            distance += segment
            if distance >= self.fuel_range_miles:
                stops.append(route_coords[i])
                distance = 0
        return stops

    def plan_stops(self, route_coords: List[Tuple[float, float]]) -> Tuple[List[dict], float]:
        stops = self._get_fuel_stop_points(route_coords)
        stop_results = []
        total_cost = 0

        for point in stops:
            station = self._find_best_station_near_point(point)
            if station:
                gallons = self.fuel_range_miles / self.mpg
                cost = station.fuel_price * gallons
                total_cost += cost

                stop_results.append({
                    'station_name': station.name,
                    'location': {
                        'lat': station.latitude,
                        'lon': station.longitude
                    },
                    'price_per_gallon': round(station.fuel_price, 2),
                    'gallons': round(gallons, 2),
                    'cost': round(cost, 2)
                })

        return stop_results, round(total_cost, 2)
