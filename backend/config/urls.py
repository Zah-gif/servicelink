from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Admin Django
    path('admin/', admin.site.urls),

    # API Users — inscription, connexion, profil
    path('api/users/', include('users.urls')),

    # API Services — catégories, métiers, communes
    path('api/services/', include('services.urls')),

    # API Reservations — réservations, avis, messages
    path('api/reservations/', include('reservations.urls')),

    # API Payments — paiements, abonnements
    path('api/payments/', include('payments.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)