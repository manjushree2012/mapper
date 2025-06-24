from django.shortcuts import render
from django.http import HttpResponse
from .serializers import RouteRequestSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

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

    


    return HttpResponse("Welcome, ! Here you canget the route from third party API")