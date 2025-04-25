from django.contrib import admin
from .models import Safari, Booking, Region, SubRegion, SafariImage, SafariItineraryItem
from .models import HomePage, Provider  # Importamos el modelo Provider

# Inlines para SafariImage y SafariItineraryItem
class SafariImageInline(admin.TabularInline):
    model = SafariImage
    extra = 1
    max_num = 10

class SafariItineraryItemInline(admin.TabularInline):
    model = SafariItineraryItem
    extra = 1

# Registros de Safari, Booking, Region, SubRegion, HomePage y Provider
@admin.register(Safari)
class SafariAdmin(admin.ModelAdmin):
    list_display = ('name', 'subregion')
    list_filter = ('subregion',)
    search_fields = ('name',)
    inlines = [SafariImageInline, SafariItineraryItemInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('safari', 'client_name', 'date', 'confirmed_by_provider')
    list_filter = ('confirmed_by_provider', 'date')
    search_fields = ('client_name', 'client_email')

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(SubRegion)
class SubRegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)

@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ('hero_title', 'why_choose_title', 'destinations_title')
    search_fields = ('hero_title', 'why_choose_title', 'destinations_title')

# Registro del modelo Provider para que sea gestionado desde el Admin
@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'whatsapp_number')  # Aquí puedes especificar qué campos mostrar
    search_fields = ('name', 'email', 'whatsapp_number')  # Permite buscar por estos campos
