from rest_framework import serializers

class RouteRequestSerializer(serializers.Serializer):
    start_location = serializers.CharField(max_length=200)
    end_location = serializers.CharField(max_length=200)