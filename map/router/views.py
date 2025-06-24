from django.shortcuts import render
from django.http import HttpResponse
from .serializers import RouteRequestSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import GeoCodeService

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

    # Go code the location so that we get respective latitide and longtitude


    


    return HttpResponse("Welcome, ! Here you canget the route from third party API")