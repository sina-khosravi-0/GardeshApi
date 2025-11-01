import hashlib
import os

from django.db import models

LOCATION_TYPE = [
    ("N", "Nature"),
    ("HH", "Historical"),
    ("R", "Restaurant"),
    ("H", "Hotel"),
    ("C", "Cafe"),
    ("S", "Shop"),
    ("PA", "Park")
]


class Location(models.Model):
    title = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    lat = models.FloatField()
    lon = models.FloatField()
    location_type = models.CharField(choices=LOCATION_TYPE, max_length=2)
    description = models.TextField(blank=True)
    helper_description = models.TextField(blank=True)
    always_open = models.BooleanField(default=False)
    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['lat', 'lon'], name='locations_lat_lon_idx'),
            models.Index(fields=['lat'], name='locations_lat_idx'),
            models.Index(fields=['lon'], name='locations_lon_idx'),
        ]


class OpeningHours(models.Model):
    WEEKDAYS = [
        ("1", "Monday"),
        ("2", "Tuesday"),
        ("3", "Wednesday"),
        ("4", "Thursday"),
        ("5", "Friday"),
        ("6", "Saturday"),
        ("7", "Sunday")
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="opening_hours")
    day = models.CharField(choices=WEEKDAYS)
    open_time = models.TimeField()
    close_time = models.TimeField()


def hash_image_path(instance, filename):
    name, ext = os.path.splitext(filename)
    hash_object = hashlib.md5(name.encode('utf-8'))
    return f"images/{instance.id}/{hash_object.hexdigest()}{ext}"

class Photo(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="photos")
    photo = models.ImageField(upload_to=hash_image_path, null=True, blank=True)
