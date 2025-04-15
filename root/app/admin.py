from django.contrib import admin
from .models import Safari, Booking

# Registra Safari solo una vez
@admin.register(Safari)
class SafariAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Solo el nombre del safari

# Registra Booking
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('safari', 'client_name', 'date', 'confirmed_by_provider')
    list_filter = ('confirmed_by_provider', 'date')
    search_fields = ('client_name', 'client_email')
