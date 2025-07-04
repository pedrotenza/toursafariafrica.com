from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Página de inicio
    path('safaris/', views.safari_list, name='safari_list'),  # Lista de safaris
    path('safari/<int:safari_id>/', views.safari_detail, name='safari_detail'),  # Detalles de un safari específico
    
    # Rutas para confirmar y cancelar booking
    path('booking/confirm/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]
