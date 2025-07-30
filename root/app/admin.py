from django.contrib import admin
from django import forms
from django.utils import timezone
from datetime import timedelta
from django.utils.html import format_html
from .models import (
    Safari,
    Booking,
    Region,
    SubRegion,
    SafariImage,
    SafariItineraryItem,
    HomePage,
    Provider,
    Participant
)

# Filtro de fecha personalizado
class DateRangeFilter(admin.SimpleListFilter):
    title = 'Date range'
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return [
            ('last_12_months', 'Last 12 months'),
            ('last_month', 'Last month'),
            ('last_week', 'Last week'),
            ('yesterday', 'Yesterday'),
            ('today', 'Today'),
            ('tomorrow', 'Tomorrow'),
            ('next_week', 'Next week'),
            ('next_month', 'Next month'),
            ('next_12_months', 'Next 12 months'),
        ]

    def queryset(self, request, queryset):
        today = timezone.now().date()
        
        if self.value() == 'last_12_months':
            last_year = today - timedelta(days=365)
            return queryset.filter(date__range=[last_year, today])
        if self.value() == 'last_month':
            last_month = today - timedelta(days=30)
            return queryset.filter(date__range=[last_month, today])
        if self.value() == 'last_week':
            last_week = today - timedelta(days=7)
            return queryset.filter(date__range=[last_week, today])
        if self.value() == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(date=yesterday)
        if self.value() == 'today':
            return queryset.filter(date=today)
        if self.value() == 'tomorrow':
            tomorrow = today + timedelta(days=1)
            return queryset.filter(date=tomorrow)
        if self.value() == 'next_week':
            next_week = today + timedelta(days=7)
            return queryset.filter(date__range=[today, next_week])
        if self.value() == 'next_month':
            next_month = today + timedelta(days=30)
            return queryset.filter(date__range=[today, next_month])
        if self.value() == 'next_12_months':
            next_year = today + timedelta(days=365)
            return queryset.filter(date__range=[today, next_year])
        return queryset

# Formulario personalizado para Participant
class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['nationality', 'age']
        widgets = {
            'age': forms.NumberInput(attrs={'step': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].widget.attrs.update({
            'type': 'number',
            'inputmode': 'numeric',  # Para teclado numérico en móviles
            'pattern': '[0-9]*',     # Patrón para validación
        })

# Inlines
class SafariImageInline(admin.TabularInline):
    model = SafariImage
    extra = 1
    max_num = 10

class SafariItineraryItemInline(admin.TabularInline):
    model = SafariItineraryItem
    extra = 1

class ParticipantInline(admin.TabularInline):
    model = Participant
    form = ParticipantForm  # Usamos el formulario personalizado
    extra = 1
    min_num = 1
    fields = ('nationality', 'age')
    verbose_name = "Participant"
    verbose_name_plural = "Participants"

@admin.register(Safari)
class SafariAdmin(admin.ModelAdmin):
    list_display = ('name', 'subregion', 'min_people', 'max_people')
    list_filter = ('subregion',)
    search_fields = ('name',)
    inlines = [SafariImageInline, SafariItineraryItemInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_number',
        'activity_date',
        'safari_name',
        'booking_date',
        'provider_name',
        'provider_response',
        'price',
        'participants_count',
        'participants_ages',
        'participants_nationalities',
        'provider_earnings',
        'your_profit',
        'client_payment',
        'client_unit_price',
        'client_name',
        'client_email',
        'client_phone',
    )
    list_filter = (
        DateRangeFilter,
        'confirmed_by_provider',
        'payment_status',
    )
    search_fields = ('booking_number', 'client_name', 'client_email', 'client_phone')
    list_per_page = 25
    list_select_related = ('safari', 'safari__provider')
    inlines = [ParticipantInline]

    # Custom templates
    change_form_template = 'admin/app/booking/change_form.html'
    change_list_template = 'admin/app/booking/change_list.html'

    def activity_date(self, obj):
        return obj.date.strftime('%d/%m/%Y') if obj.date else '—'
    activity_date.short_description = 'Date'
    activity_date.admin_order_field = 'date'

    def safari_name(self, obj):
        return obj.safari.name if obj.safari else '—'
    safari_name.short_description = 'Activity'

    def participants_count(self, obj):
        return obj.number_of_people
    participants_count.short_description = 'Part'

    def participants_ages(self, obj):
        participants = obj.participants.all()
        if not participants.exists():
            return "—"
        ages = [str(p.age) for p in participants if p.age is not None]
        return format_html("<br>".join(ages))
    participants_ages.short_description = 'Ages'

    def participants_nationalities(self, obj):
        participants = obj.participants.all()
        if not participants.exists():
            return "—"
        nationalities = [p.nationality for p in participants if p.nationality]
        return format_html("<br>".join(nationalities))
    participants_nationalities.short_description = 'Nationalities'

    def booking_date(self, obj):
        return obj.booking_datetime.strftime('%d/%m/%Y %H:%M') if obj.booking_datetime else '—'
    booking_date.short_description = 'Booking Date'

    def provider_name(self, obj):
        return obj.safari.provider.name if obj.safari and obj.safari.provider else '—'
    provider_name.short_description = 'Provider'

    def provider_response(self, obj):
        if obj.provider_response_date:
            response_time = obj.provider_response_date.strftime('%d/%m/%Y %H:%M')
            if obj.confirmed_by_provider:
                return format_html('<span style="color: green;">{} (Accepted)</span>', response_time)
            elif obj.confirmed_by_provider is False:
                return format_html('<span style="color: red;">{} (Rejected)</span>', response_time)
        return format_html('<span style="color: orange;">Pending</span>')
    provider_response.short_description = 'Prov Resp'

    def price(self, obj):
        if obj.safari and obj.safari.provider_price:
            return f"{obj.safari.provider_price:.2f}"
        return "—"
    price.short_description = 'Price'

    def provider_earnings(self, obj):
        if obj.safari and obj.safari.provider_price:
            amount = obj.safari.provider_price * obj.number_of_people
            return format_html('<span style="color: black;">{}</span>', f"{amount:.2f}")
        return "—"
    provider_earnings.short_description = 'Prov Earns'

    def your_profit(self, obj):
        if obj.safari and obj.safari.provider_price and obj.payment_amount:
            cost = obj.safari.provider_price * obj.number_of_people
            profit = obj.payment_amount - cost
            return format_html('<span style="color: green;">{}</span>', f"{profit:.2f}")
        return "—"
    your_profit.short_description = 'Profit'

    def client_payment(self, obj):
        if obj.payment_amount: 
            return format_html('<span style="color: black;">{}</span>', f"{obj.payment_amount:.2f}")
        return "—"
    client_payment.short_description = 'Client Pay'

    def client_unit_price(self, obj):
        if obj.safari and obj.safari.client_price:
            return f"{obj.safari.client_price:.2f}"
        return "—"
    client_unit_price.short_description = 'Unit Price'

    def client_name(self, obj):
        return obj.client_name if obj.client_name else '—'
    client_name.short_description = 'Client'

    def client_email(self, obj):
        return obj.client_email if obj.client_email else '—'
    client_email.short_description = 'Email'

    def client_phone(self, obj):
        return obj.client_phone if obj.client_phone else '—'
    client_phone.short_description = 'Phone'

    class Media:
        css = {
            'all': ('app/css/admin_custom.css?v=2.1',)
        }
        js = ('app/js/admin_custom.js?v=2.1',)

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
    list_per_page = 20