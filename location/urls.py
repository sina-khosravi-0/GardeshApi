from django.urls import path

from location.views import AllLocationsListAPIView, SearchLocationListAPIView, ProximityLocationListAPIView, \
    LocationDetailAPIView

urlpatterns = [
    path('all/', AllLocationsListAPIView.as_view()),
    path('search/', SearchLocationListAPIView.as_view()),
    path('nearme/', ProximityLocationListAPIView.as_view()),
    path('get/<int:id>/', LocationDetailAPIView.as_view()),
]
