
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from smart_football_center.accounts.views import (
    UserViewSet, LoginView, LogoutView, RegisterView,
    CoachViewSet, PlayerViewSet
)
from smart_football_center.teams.views import TeamViewSet
from smart_football_center.bookings.views import (
    SessionViewSet, BookingViewSet, BundleViewSet,
    MembershipViewSet, DiscountViewSet
)


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'coaches', CoachViewSet, basename='coach')
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'teams', TeamViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'bundles', BundleViewSet)
router.register(r'memberships', MembershipViewSet)
router.register(r'discounts', DiscountViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),

    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)
