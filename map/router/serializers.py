from rest_framework import serializers

class RouteRequestSerializer(serializers.Serializer):
    start_location = serializers.CharField(
        max_length=200, 
        help_text="Starting location (e.g., 'New York, NY' or '123 Main St, Boston, MA')"
    )
    end_location = serializers.CharField(
        max_length=200, 
        help_text="Ending location (e.g., 'Los Angeles, CA' or '456 Oak Ave, Seattle, WA')"
    )