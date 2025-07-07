from django.contrib import admin
from django.utils.html import format_html
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

# Inlines
class SafariImageInline(admin.TabularInline):
    model = SafariImage
    extra = 1
    max_num = 10

class SafariItineraryItemInline(admin.TabularInline):
    model = SafariItineraryItem
    extra = 1

@admin.register(Safari)
class SafariAdmin(admin.ModelAdmin):
    list_display = ('name', 'subregion')
    list_filter = ('subregion',)
    search_fields = ('name',)
    inlines = [SafariImageInline, SafariItineraryItemInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'safari_date',
        'safari_name',
        'display_number_of_people',
        'booking_date',
        'provider_name',
        'provider_response_datetime',
        'display_client_name',
        'display_client_email',
        'display_phone',
        'display_client_nationality',
        'display_client_age',
    )
    list_filter = ('confirmed_by_provider', 'date')
    search_fields = ('client_name', 'client_email', 'client_phone')
    list_per_page = 25  # Paginación mejorada

    # Plantillas personalizadas
    change_form_template = 'admin/app/booking/change_form.html'
    change_list_template = 'admin/app/booking/change_list.html'

    def safari_date(self, obj):
        return obj.date.strftime('%d/%m/%Y') if obj.date else '—'
    safari_date.short_description = 'Safari Date'
    safari_date.admin_order_field = 'date'

    def safari_name(self, obj):
        return obj.safari.name if obj.safari else '—'
    safari_name.short_description = 'Safari'
    safari_name.admin_order_field = 'safari__name'

    def display_number_of_people(self, obj):
        return obj.number_of_people
    display_number_of_people.short_description = 'Participants'
    display_number_of_people.admin_order_field = 'number_of_people'

    def booking_date(self, obj):
        return obj.booking_datetime.strftime('%d/%m/%Y %H:%M') if obj.booking_datetime else '—'
    booking_date.short_description = 'Booking Date'
    booking_date.admin_order_field = 'booking_datetime'

    def provider_name(self, obj):
        return obj.safari.provider.name if obj.safari and obj.safari.provider else '—'
    provider_name.short_description = 'Provider'
    provider_name.admin_order_field = 'safari__provider__name'

    def provider_response_datetime(self, obj):
        return obj.provider_response_date.strftime('%d/%m/%Y %H:%M') if obj.provider_response_date else '—'
    provider_response_datetime.short_description = 'Provider Response Date'
    provider_response_datetime.admin_order_field = 'provider_response_date'

    def display_client_name(self, obj):
        return obj.client_name if obj.client_name else '—'
    display_client_name.short_description = 'Client'
    display_client_name.admin_order_field = 'client_name'

    def display_client_email(self, obj):
        return obj.client_email if obj.client_email else '—'
    display_client_email.short_description = 'E mail'
    display_client_email.admin_order_field = 'client_email'

    def display_phone(self, obj):
        return obj.client_phone if obj.client_phone else '—'
    display_phone.short_description = 'Phone'
    display_phone.admin_order_field = 'client_phone'

    def display_client_nationality(self, obj):
        return obj.client_nationality if obj.client_nationality else '—'
    display_client_nationality.short_description = 'Nationality'
    display_client_nationality.admin_order_field = 'client_nationality'

    def display_client_age(self, obj):
        return obj.client_age if obj.client_age else '—'
    display_client_age.short_description = 'Age'
    display_client_age.admin_order_field = 'client_age'

    class Media:
        css = {
            'all': ('app/css/admin_custom.css',)
        }
        js = ('app/js/admin_custom.js',)  # Ruta corregida

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_filters_button'] = True  # Variable para la plantilla
        return super().changelist_view(request, extra_context=extra_context)

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

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'whatsapp_number')
    search_fields = ('name', 'email', 'whatsapp_number')