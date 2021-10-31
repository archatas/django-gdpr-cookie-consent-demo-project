from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path(
        "cookies/",
        include("gdpr_cookie_consent.urls", namespace="cookie_consent"),
    ),
    path("admin/", admin.site.urls),
]
