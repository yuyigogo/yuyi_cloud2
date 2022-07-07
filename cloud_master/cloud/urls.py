"""cloud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("rest/v1/admin/", admin.site.urls),
]

# every app should has its own urls.py and insert it below
urlpatterns += [
    path("rest/v1/", include("user_management.urls")),
    path("rest/v1/", include("customer.urls")),
    path("rest/v1/", include("sites.urls")),
    path("rest/v1/", include("equipment_management.urls")),
    path("rest/v1/", include("file_management.urls")),
    path("rest/v1/", include("navigation.urls")),
    path("rest/v1/", include("cloud_ws.urls")),
]
