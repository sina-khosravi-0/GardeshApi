from django.contrib import admin

from location.models import Location, OpeningHours, Photo


class OpeningHoursInline(admin.TabularInline):
    model = OpeningHours


class PhotoInline(admin.TabularInline):
    model = Photo


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = [OpeningHoursInline, PhotoInline]
