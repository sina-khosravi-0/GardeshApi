import math
from typing import List, Tuple
from django.db.models import QuerySet
from .models import Location

EARTH_KM = 6371.0

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance between (lat1,lon1) and (lat2,lon2) in kilometers."""
    # convert degrees to radians
    lat1_r = math.radians(lat1)
    lon1_r = math.radians(lon1)
    lat2_r = math.radians(lat2)
    lon2_r = math.radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2.0) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_KM * c

def bbox_for_radius_km(lat: float, lon: float, radius_km: float) -> Tuple[float, float, float, float]:
    """
    Return (min_lat, max_lat, min_lon, max_lon) bounding box in degrees for given radius in km.
    Uses approximate conversions: 1 degree latitude ≈ 111 km; longitude degrees vary by latitude.
    """
    # 1 deg latitude is approximately 111 km
    lat_delta = radius_km / 111.0

    # longitude delta depends on latitude
    # cos(latitude) factor (latitude must be converted to radians)
    lat_r = math.radians(lat)
    lon_delta = radius_km / (111.0 * math.cos(lat_r)) if math.cos(lat_r) != 0 else 180.0

    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lon = lon - lon_delta
    max_lon = lon + lon_delta

    # normalize longitudes to [-180, 180] if you want — simple clamp for MVP
    if min_lon < -180.0:
        min_lon = -180.0
    if max_lon > 180.0:
        max_lon = 180.0

    return min_lat, max_lat, min_lon, max_lon

def nearest_locations_by_point(lat: float, lon: float, k: int = 100, radius_km: float = 10.0,
                               location_types: List[str] = None, exclude_id: int = None) -> List[dict]:
    """
    Returns up to k nearest Location rows (as dicts) to (lat, lon).
    - radius_km: maximum radius to consider (uses bbox + exact distance)
    - location_types: optional list to filter by location_type
    - exclude_id: optional id to exclude (for when searching near a site)
    """
    min_lat, max_lat, min_lon, max_lon = bbox_for_radius_km(lat, lon, radius_km)

    qs: QuerySet = Location.objects.filter(lat__gte=min_lat, lat__lte=max_lat,
                                           lon__gte=min_lon, lon__lte=max_lon)
    if location_types:
        qs = qs.filter(location_type__in=location_types)
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)

    # Only fetch necessary fields to reduce memory / transfer
    qs = qs.only('id', 'lat', 'lon')
    # Evaluate queryset — should be small after bbox filter
    candidates = list(qs)

    # Compute exact distances in Python
    results = []
    for loc in candidates:
        d_km = haversine_distance_km(lat, lon, loc.lat, loc.lon)
        if d_km <= radius_km:
            results.append({
                'id': loc.id,
                'title': loc.title,
                'distance_km': d_km,
            })

    # Sort and return top-k
    results.sort(key=lambda x: x['distance_km'])
    return results[:k]
