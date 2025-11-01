from django.db.models import Q
from django.http import HttpRequest
from django.template.defaultfilters import title
from rest_framework import generics

from location import utils
from location.models import Location
from location.serializers import LocationSerializer, NearestLocationSerializer


class AllLocationsListAPIView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_queryset(self):
        queryset = Location.objects.filter(location_type__in=["N", "HH", "PA"])[:10]
        return queryset


class LocationDetailAPIView(generics.RetrieveAPIView):
    serializer_class = LocationSerializer

    def get_object(self):
        location = Location.objects.get(id=self.kwargs['id'])
        return location

    def get_serializer_context(self):
        location = Location.objects.get(id=self.kwargs['id'])
        nearests = utils.nearest_locations_by_point(location.lat, location.lon,
                                                    radius_km=1,
                                                    exclude_id=location.id)

        distance_map = {item['id']: item['distance_km'] for item in nearests}
        ids = [item['id'] for item in nearests]
        queryset = Location.objects.filter(id__in=ids)
        for loc in queryset:
            loc.distance_km = distance_map.get(loc.id, None)

        # Get the base context (e.g., includes 'request' by default)
        context = super().get_serializer_context()

        # Prepare your list here (example: dynamic based on request or fixed)
        featured_categories = nearests  # Your list

        # Pass it via context
        context['featured_categories'] = featured_categories
        return context


class SearchLocationListAPIView(generics.ListAPIView):
    serializer_class = LocationSerializer

    def get_queryset(self):
        location_type = None
        try:
            location_type = self.request.GET['location_type']
        except:
            pass
        query = self.request.GET['q']
        queryset = Location.objects.filter(
            Q(title__icontains=query) | Q(description__contains=query) | Q(helper_description__contains=query))
        if location_type is not None:
            queryset = queryset.filter(location_type=location_type)

        return queryset


class ProximityLocationListAPIView(generics.ListAPIView):
    serializer_class = NearestLocationSerializer

    def get_queryset(self):
        nearests = utils.nearest_locations_by_point(float(self.request.GET['lat']), float(self.request.GET['lon']),
                                                    radius_km=int(self.request.GET['km']))

        distance_map = {item['id']: item['distance_km'] for item in nearests}
        ids = [item['id'] for item in nearests]
        queryset = Location.objects.filter(id__in=ids)
        for obj in queryset:
            obj.distance_km = distance_map.get(obj.id, None)

        return queryset
