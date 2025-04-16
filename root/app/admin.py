from django.contrib import admin
from .models import Safari, Booking, Region, SubRegion

# Admin para Safari
@admin.register(Safari)
class SafariAdmin(admin.ModelAdmin):
    list_display = ('name', 'subregion')  # Mostrar subregión también
    list_filter = ('subregion',)
    search_fields = ('name',)

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
