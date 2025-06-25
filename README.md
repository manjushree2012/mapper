# Spotter Maps

Spotter Maps is a simple application that calculates optimized route with fuel stations for all over the US. Given a start point and end point, it suggests a optimal route with fuel stations and directions.

## Technologies Used

- Django 3.2.23
- Django REST Framework
- OpenRouteService API
- Redis
- Python libraries:
  - geopy (distance calculations)
  - shapely (geometric operations)
  - requests (API communication)
  - and others ... (see requirements.txt for the list)
## API Endpoints

### Route Planning Endpoint

```
POST /api/route/
```

Request body:
```json
{
    "start_location": "New York, NY",
    "end_location": "Los Angeles, CA"
}
```

Response includes:
- Complete route information
- Optimal fuel stops with prices
- Total journey cost estimation
- Navigation instructions

## Performance Optimizations

1. Geocoding results cached in Redis
2. Route polygon buffering for efficient fuel station filtering
3. Spatial indexing for quick nearest station searches
4. Single API call for route calculation

## Limitations

1. Caching mechanism used here cannot be used in a real prod scenario. This is because we are considering a simple string search for getting co-ordinates for a place whereas for a real application, the calculation would be much more complex.
2. I have taken the liberty of using some mock data in CSV as well for fuel stations.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Redis server
4. Configure environment variables:
   - Create .env file
   - Add OpenRouteService API key: `ORS_API_KEY=your-key-here`
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```