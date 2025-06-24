from django.shortcuts import render
from django.http import HttpResponse
from .serializers import RouteRequestSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import GeoCodeService, RouteService

@api_view(['POST'])
def get_route(request):
    """
    Get route between two places (start and end)
    """

    serializer = RouteRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": "Invalid input", "details": serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    start_location = serializer.validated_data['start_location']
    end_location = serializer.validated_data['end_location']

    # Step 1: Get co-ordinates of starting point
    geo_code_service = GeoCodeService()
    start_location_cords = geo_code_service.geocode(start_location)
    print(start_location_cords)
    if not start_location_cords:
         return Response(
                {"error": f"Could not find coordinates for start location: {start_location}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Step 2: Get co-ordinates of ending point
    end_location_cords = geo_code_service.geocode(end_location)
    print(end_location_cords)
    if not end_location_cords:
         return Response(
                {"error": f"Could not find coordinates for end location: {end_location}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

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
    
    # Prepare response
    response_data = {
        'start_location': start_location,
        'end_location': end_location,
        'start_coordinates': [start_location_cords[0], start_location_cords[1]],  # [lat, lon]
        'end_coordinates': [end_location_cords[0], end_location_cords[1]],        # [lat, lon]
        'total_distance_miles': round(distance_miles, 2),
        'total_distance_km': round(distance_km, 2),
        'total_duration_minutes': round(duration_minutes, 2),
        'total_duration_hours': round(duration_hours, 2),
        'route_geometry': route['geometry'],
        'route_instructions': route.get('segments', [{}])[0].get('steps', [])
    }
        
    return Response(response_data, status=status.HTTP_200_OK)