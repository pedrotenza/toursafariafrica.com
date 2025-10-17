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
    # VISTA ADMIN/PROVEEDOR - SIN precios
    path('booking/confirm/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    
    # VISTA ADMIN/PROVEEDOR - SIN precios  
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    # VISTA CLIENTE - CON precios
    path('booking/confirmed/<str:booking_number>/', views.booking_confirmed, name='booking_confirmed'),

    # ✅ AÑADE ESTA LÍNEA FALTANTE:
    path('booking/cancelled/<str:booking_number>/', views.booking_cancelled, name='booking_cancelled'),

    # VISTA ADMIN/PROVEEDOR - SIN precios (alias corto)
    path('confirm/<int:booking_id>/', views.confirm_booking, name='confirm_booking_short'),
]