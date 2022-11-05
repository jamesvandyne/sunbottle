from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("sunbottle.interfaces.api.urls")),
    path("", include("sunbottle.interfaces.public.site.urls")),
]
