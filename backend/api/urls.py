from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'recordings', views.VoiceRecordingViewSet, basename='recording')
router.register(r'analysis', views.AnalysisResultViewSet, basename='analysis')
router.register(r'profile', views.UserProfileViewSet, basename='profile')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', views.current_user, name='current_user'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
    
    # Include router URLs
    path('', include(router.urls)),
]
