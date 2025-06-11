from django.urls import include, path, re_path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
urlpatterns = [
    path('', include(router.urls)),
    path('login', views.line_login),
    path('callback', views.line_callback),
]