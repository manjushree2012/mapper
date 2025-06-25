from rest_framework.response import Response
from rest_framework import status
from .serializers import RouteRequestSerializer
from .services import GeoCodeService

class RouteValidationService:
    def __init__(self):
        self.geo_code_service = GeoCodeService()

    def validate_request(self, request_data):
        """Validate the route request data and return validated locations"""
        serializer = RouteRequestSerializer(data=request_data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        return serializer.validated_data

    def validate_coordinates(self, start_location, end_location):
        """Validate and get coordinates for start and end locations"""
        # Validate start location
        start_location_cords = self.geo_code_service.geocode(start_location)
        if not start_location_cords:
            return Response(
                {"error": f"Could not find coordinates for start location: {start_location}"},
                status=status.HTTP_400_BAD_REQUEST
            ), None, None

        # Validate end location
        end_location_cords = self.geo_code_service.geocode(end_location)
        if not end_location_cords:
            return Response(
                {"error": f"Could not find coordinates for end location: {end_location}"},
                status=status.HTTP_400_BAD_REQUEST
            ), None, None

        return None, start_location_cords, end_location_cords