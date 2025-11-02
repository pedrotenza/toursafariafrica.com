from django.urls import path
from . import views

urlpatterns = [
    # ==============================
    # Páginas principales
    # ==============================
    path('', views.home, name='home'),
    path('safaris/', views.safari_list, name='safari_list'),
    path('safari/<int:safari_id>/', views.safari_detail, name='safari_detail'),

    # ==============================
    # Gestión de reservas (Booking)
    # ==============================
    path('booking/confirm/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking/confirmed/<str:booking_number>/', views.booking_confirmed, name='booking_confirmed'),
    path('booking/cancelled/<str:booking_number>/', views.booking_cancelled, name='booking_cancelled'),
    path('confirm/<int:booking_id>/', views.confirm_booking, name='confirm_booking_short'),

    # ==============================
    # Términos del proveedor
    # ==============================
    path('provider-terms/<int:booking_id>/', views.provider_terms_view, name='provider_terms'),

    # ==============================
    # Términos del cliente
    # ==============================
    path('client-terms/', views.client_terms_view, name='client_terms'),
]
