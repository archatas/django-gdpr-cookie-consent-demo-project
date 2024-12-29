from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("test/", TemplateView.as_view(template_name="test.html"), name="test"),
    path(
        "cookies/",
        include("gdpr_cookie_consent.urls", namespace="cookie_consent"),
    ),
    path("admin/", admin.site.urls),
]
