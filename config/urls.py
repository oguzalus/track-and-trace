"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include, reverse
from django.http.response import JsonResponse

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from shipments.rest.router import urls as shipment_urls

def index(request):
    return JsonResponse(
        {
            "message": "Hello, world. You're at the track_and_trace index.",
            "endpoints": {
                "shipments": f"{request.build_absolute_uri(reverse('shipment-list'))}",
                "schema": f"{request.build_absolute_uri(reverse('schema'))}",
                "swagger": f"{request.build_absolute_uri(reverse('swagger-ui'))}",
                "redoc": f"{request.build_absolute_uri(reverse('redoc'))}",
            },
        },
    )

urlpatterns = [
    path('', index),
    path('api-auth/', include('rest_framework.urls')),
    path("admin/", admin.site.urls),

    # V1 API
    path('v1/', include(shipment_urls)),
    # OpenAPI schema
    path('v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger and Redoc UI
    path('v1/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
