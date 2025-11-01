from rest_framework import serializers

from location.models import Location, Photo, OpeningHours


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        exclude = ('location', 'id')


class OpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        exclude = ('location', 'id')


class LocationSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    opening_hours = OpeningHoursSerializer(many=True, read_only=True)
    nearest_locations = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = '__all__'

    def get_nearest_locations(self, obj):
        featured_list = self.context.get('featured_categories', [])
        return featured_list


class NearestLocationSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    opening_hours = OpeningHoursSerializer(many=True, read_only=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = '__all__'

    def get_distance_km(self, obj):
        return getattr(obj, 'distance_km', None)
