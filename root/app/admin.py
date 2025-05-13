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

# Registro del modelo Safari
@admin.register(Safari)
class SafariAdmin(admin.ModelAdmin):
    list_display = ('name', 'subregion')
    list_filter = ('subregion',)
    search_fields = ('name',)
    inlines = [SafariImageInline, SafariItineraryItemInline]

# Registro del modelo Booking con estado legible
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('safari', 'client_name', 'date', 'estado_reserva')
    list_filter = ('confirmed_by_provider', 'date')
    search_fields = ('client_name', 'client_email')

    def estado_reserva(self, obj):
        return "Confirmada" if obj.confirmed_by_provider else "Demanda de reserva"
    estado_reserva.short_description = "Estado"

# Registro del modelo Region
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Registro del modelo SubRegion
@admin.register(SubRegion)
class SubRegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)

# Registro del modelo HomePage
@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ('hero_title', 'why_choose_title', 'destinations_title')
    search_fields = ('hero_title', 'why_choose_title', 'destinations_title')

# Registro del modelo Provider
@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'whatsapp_number')
    search_fields = ('name', 'email', 'whatsapp_number')
