"""
URL configuration for LMS project - API-only backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView,BulkImportAPIView,bulk_import_test_ui

urlpatterns = [
    # Root redirect to API
    path('', RedirectView.as_view(url='/api/labs/', permanent=False)),

    # App-specific endpoints
    path('api/users/', include('users.urls')),
    path('api/tickets/', include('tickets.urls')),
    path('api/notifications/', include('notifications.urls')),


    # Admin interface
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include('labs.urls')),

    # Authentication endpoints
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Bulk import endpoint
    path('api/import/', BulkImportAPIView.as_view(), name='bulk-import'),
    path("api/import-ui/", bulk_import_test_ui, name="bulk-import-ui"),
]
