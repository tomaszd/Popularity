# Create a router and register our viewsets with it.
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from popularity import views

router = DefaultRouter()
router.register(r'repos', views.RepoViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
