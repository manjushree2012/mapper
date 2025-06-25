# Standard library imports
import os

# Django imports
from django.conf import settings

# Third-party imports
from openrouteservice import convert
from shapely.geometry import LineString
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Local application imports
from .services import FuelPlannerService, RouteService
from .validation import RouteValidationService


@api_view(['POST'])
def get_route(request):
    """
    Get route between two places (start and end)
    """
    validation_service = RouteValidationService()
    validated_data = validation_service.validate_request(request.data)
    if isinstance(validated_data, Response):
        return validated_data
    
    # Validate and get coordinates
    error_response, start_location_cords, end_location_cords = validation_service.validate_coordinates(
        validated_data['start_location'],
        validated_data['end_location']
    )
    if error_response:
        return error_response

    # Step 3: Now get the route from start to end point
    route_service = RouteService()
    route_data = route_service.get_route(start_location_cords,end_location_cords)
    if not route_data or 'routes' not in route_data:
        return Response(
            {"error": "Could not calculate route between the given locations"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Step 4: Extract rouute information
    route = route_data['routes'][0]
    summary = route['summary']
    
    # Convert distances and durations
    distance_meters = summary['distance']
    duration_seconds = summary['duration']
    
    distance_km = distance_meters / 1000
    distance_miles = distance_km * 0.621371
    duration_minutes = duration_seconds / 60
    duration_hours = duration_minutes / 60

    # Decode the polyline to a list of (lat, lon) tuples
    route_coords = convert.decode_polyline(route['geometry'])

    # Convert to LineString and buffer to get polygon
    line = LineString([(pt[1], pt[0]) for pt in route_coords['coordinates']])  # (lon, lat)
    route_polygon = line.buffer(0.1) #Create a buffer around that route


    csv_path = os.path.join(settings.BASE_DIR, 'data', 'fuel-prices.csv')  # if stored in /data/
    fuel_planner = FuelPlannerService(csv_path=csv_path, route_polygon=route_polygon)

    raw_coords = route_coords['coordinates']
    coords_latlon = [(coord[1], coord[0]) for coord in raw_coords]
    fuel_stops, total_cost = fuel_planner.plan_stops(coords_latlon)

    # Prepare response
    response_data = {
        'start_location': validated_data['start_location'],
        'end_location': validated_data['end_location'],
        'start_coordinates': [start_location_cords[0], start_location_cords[1]],  # [lat, lon]
        'end_coordinates': [end_location_cords[0], end_location_cords[1]],        # [lat, lon]
        'total_distance_miles': round(distance_miles, 2),
        'total_distance_km': round(distance_km, 2),
        'total_duration_minutes': round(duration_minutes, 2),
        'total_duration_hours': round(duration_hours, 2),
        'route_geometry': route['geometry'],
        'route_instructions': route.get('segments', [{}])[0].get('steps', []),
        'total_fuel_cost': total_cost,
        'fuel_stops': fuel_stops,
    }
        
    return Response(response_data, status=status.HTTP_200_OK)