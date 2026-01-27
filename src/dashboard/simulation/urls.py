from django.urls import path

from . import views


urlpatterns = [
    path("telemetry/", views.telemetry_ingest, name="telemetry-ingest"),
    path("telemetry/recent/", views.telemetry_recent, name="telemetry-recent"),
    path("commands/", views.commands, name="commands"),
]

