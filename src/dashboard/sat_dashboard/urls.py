from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("simulation.urls")),
    # Catch-all: serve the React SPA entrypoint
    re_path(r"^.*$", TemplateView.as_view(template_name="index.html"), name="spa-entry"),
]

