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

# Admin de Booking con campos personalizados y orden corregido
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'safari_date',           # Fecha del Safari (del campo date)
        'safari_name',           # Nombre del Safari
        'booking_date',          # Fecha Reserva (repetida porque solo hay date)
        'provider_name',         # Operador
        'provider_response_datetime',  # Respuesta Operador
        'client_name',
        'client_email',
        'client_phone',
        'client_nationality',
        'client_age',
    )
    list_filter = ('confirmed_by_provider', 'date')
    search_fields = ('client_name', 'client_email', 'client_phone')

    def safari_date(self, obj):
        return obj.date.strftime('%d/%m/%Y') if obj.date else '—'
    safari_date.short_description = 'Fecha Safari'
    safari_date.admin_order_field = 'date'

    def safari_name(self, obj):
        return obj.safari.name if obj.safari else '—'
    safari_name.short_description = 'Safari'
    safari_name.admin_order_field = 'safari__name'

    def booking_date(self, obj):
        return obj.date.strftime('%d/%m/%Y') if obj.date else '—'
    booking_date.short_description = 'Fecha Reserva'
    booking_date.admin_order_field = 'date'

    def provider_name(self, obj):
        return obj.safari.provider.name if obj.safari and obj.safari.provider else '—'
    provider_name.short_description = 'Operador'
    provider_name.admin_order_field = 'safari__provider__name'

    def provider_response_datetime(self, obj):
        return obj.provider_response_date.strftime('%d/%m/%Y %H:%M') if obj.provider_response_date else '—'
    provider_response_datetime.short_description = 'Respuesta Operador'
    provider_response_datetime.admin_order_field = 'provider_response_date'

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
