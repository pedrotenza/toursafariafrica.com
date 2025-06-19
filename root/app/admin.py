from django.contrib import admin
from .models import (
    Safari,
    Booking,
    Region,
    SubRegion,
    SafariImage,
    SafariItineraryItem,
    HomePage,
    Provider
)

# Inlines para SafariImage y SafariItineraryItem
class SafariImageInline(admin.TabularInline):
    model = SafariImage
    extra = 1
    max_num = 10

class SafariItineraryItemInline(admin.TabularInline):
    model = SafariItineraryItem
    extra = 1

# Admin de Safari
@admin.register(Safari)
class SafariAdmin(admin.ModelAdmin):
    list_display = ('name', 'subregion')
    list_filter = ('subregion',)
    search_fields = ('name',)
    inlines = [SafariImageInline, SafariItineraryItemInline]

# Admin de Booking con campos personalizados
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'safari_name',
        'booking_datetime',
        'provider_name',
        'provider_response_datetime',
        'client_name',
        'client_email',
        'client_phone',
        'client_nationality',
        'client_age',
    )
    list_filter = ('confirmed_by_provider', 'date')
    search_fields = ('client_name', 'client_email', 'client_phone')

    def safari_name(self, obj):
        return obj.safari.name
    safari_name.short_description = 'Safari'

    def provider_name(self, obj):
        return obj.safari.provider.name if obj.safari.provider else '—'
    provider_name.short_description = 'Operador'

    def booking_datetime(self, obj):
        # Muestra fecha y hora si es DateTimeField; si es DateField, solo muestra fecha
        return obj.date.strftime('%d/%m/%Y %H:%M') if hasattr(obj.date, 'strftime') else obj.date
    booking_datetime.short_description = 'Fecha Reserva'

    def provider_response_datetime(self, obj):
        return obj.provider_response_date.strftime('%d/%m/%Y %H:%M') if obj.provider_response_date else '—'
    provider_response_datetime.short_description = 'Respuesta Operador'

# Admin de Region
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Admin de SubRegion
@admin.register(SubRegion)
class SubRegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)

# Admin de HomePage
@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ('hero_title', 'why_choose_title', 'destinations_title')
    search_fields = ('hero_title', 'why_choose_title', 'destinations_title')

# Admin de Provider
@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'whatsapp_number')
    search_fields = ('name', 'email', 'whatsapp_number')
