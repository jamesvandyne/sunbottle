from django.urls import include, path

urlpatterns = [path("", include("sunbottle.interfaces.public.site.urls"))]
