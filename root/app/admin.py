from django.contrib import admin
from .models import Safari, Booking, Region, SubRegion, SafariImage

# Inline para imágenes de Safari
class SafariImageInline(admin.TabularInline):
    model = SafariImage
    extra = 1
    max_num = 10  # Opcional: limitar cantidad de imágenes por safari

# Admin para Safari con imágenes
@admin.register(Safari)
class SafariAdmin(admin.ModelAdmin):
    list_display = ('name', 'subregion')
    list_filter = ('subregion',)
    search_fields = ('name',)
    inlines = [SafariImageInline]

# Admin para Booking
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('safari', 'client_name', 'date', 'confirmed_by_provider')
    list_filter = ('confirmed_by_provider', 'date')
    search_fields = ('client_name', 'client_email')

# Admin para Region
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Admin para SubRegion
@admin.register(SubRegion)
class SubRegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)
