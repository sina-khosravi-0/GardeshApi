from django.urls import path

from assistant.views import prompt_view

urlpatterns = [
    path('prompt/', prompt_view),
]