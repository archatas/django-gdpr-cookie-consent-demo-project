from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.views.generic import TemplateView, RedirectView


def test_view(request):
    if "ok" not in request.session:
        request.session["ok"] = "OK"
    return render(request, "test.html")


urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "img/favicon.ico"), name="favicon"),
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("test/", test_view, name="test"),
    path(
        "cookies/",
        include("gdpr_cookie_consent.urls", namespace="cookie_consent"),
    ),
    path("admin/", admin.site.urls),
]
