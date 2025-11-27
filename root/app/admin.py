from django.contrib import admin
from django import forms
from django.utils import timezone
from datetime import timedelta
from django.utils.html import format_html
from django.db.models import Value
from django.db.models.functions import Concat
from django.urls import path
from django.template.response import TemplateResponse
from .models import (
    Safari, Booking, Region, SubRegion, SafariImage,
    SafariItineraryItem, HomePage, Provider, Participant
)

# ===============================
# Filtro personalizado por fechas
# ===============================
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
        mapping = {
            'last_12_months': today - timedelta(days=365),
            'last_month': today - timedelta(days=30),
            'last_week': today - timedelta(days=7),
            'yesterday': today - timedelta(days=1),
        }
        if self.value() in mapping:
            return queryset.filter(date__range=[mapping[self.value()], today])
        elif self.value() == 'today':
            return queryset.filter(date=today)
        elif self.value() == 'tomorrow':
            return queryset.filter(date=today + timedelta(days=1))
        elif self.value() == 'next_week':
            return queryset.filter(date__range=[today, today + timedelta(days=7)])
        elif self.value() == 'next_month':
            return queryset.filter(date__range=[today, today + timedelta(days=30)])
        elif self.value() == 'next_12_months':
            return queryset.filter(date__range=[today, today + timedelta(days=365)])
        return queryset

# ===============================
# Formularios personalizados
# ===============================
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'
        widgets = {
            'client_phone_prefix': forms.TextInput(attrs={
                'placeholder': '+34',
                'style': 'width: 80px;'
            }),
            'client_phone_number': forms.TextInput(attrs={
                'placeholder': '612345678',
                'style': 'width: 150px;'
            }),
        }


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
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
        })

# ===============================
# Inlines
# ===============================
class SafariImageInline(admin.TabularInline):
    model = SafariImage
    extra = 1
    max_num = 10


class SafariItineraryItemInline(admin.TabularInline):
    model = SafariItineraryItem
    extra = 1


class ParticipantInline(admin.TabularInline):
    model = Participant
    form = ParticipantForm
    extra = 1
    min_num = 1
    fields = ('nationality', 'age')
    verbose_name = "Participant"
    verbose_name_plural = "Participants"

# ===============================
# ADMIN: Safari
# ===============================
@admin.register(Safari)
class SafariAdmin(admin.ModelAdmin):
    list_display = ('name', 'subregion', 'min_people', 'max_people')
    list_filter = ('subregion',)
    search_fields = ('name',)
    inlines = [SafariImageInline, SafariItineraryItemInline]

# ===============================
# ADMIN: Booking
# ===============================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingForm

    list_display = (
        'booking_number', 'activity_date', 'safari_name', 'booking_date',
        'provider_name', 'status_colored',  # Estado con colores + fecha/hora en negro
        'provider_accept_terms', 'client_accept_terms',
        'participants_count', 'participants_ages', 'participants_nationalities',
        'price', 'provider_earnings', 'your_profit',
        'client_payment', 'client_unit_price',
        'client_name', 'client_email', 'formatted_client_phone',
    )

    list_filter = (
        DateRangeFilter, 'confirmed_by_provider', 'payment_status',
    )

    search_fields = (
        'booking_number', 'client_name', 'client_email',
        'safari__name', 'safari__provider__name',
    )

    list_per_page = 25
    list_select_related = ('safari', 'safari__provider')
    inlines = [ParticipantInline]

    fieldsets = (
        (None, {
            'fields': (
                'safari', 'date', 'number_of_people',
                ('client_name', 'client_email'),
                ('client_phone_prefix', 'client_phone_number'),
                'payment_status', 'payment_amount', 'payment_method',
                'transaction_id'
            )
        }),
        ('Provider Confirmation', {
            'classes': ('collapse',),
            'fields': (
                'confirmed_by_provider', 'provider_response_date',
                'provider_accepted_terms', 'provider_acceptance_datetime',
                'provider_acceptance_ip', 'provider_acceptance_text',
                'provider_acceptance_user_agent',
            ),
        }),
    )

    # ==========================
    # URLs personalizadas
    # ==========================
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:booking_id>/provider_acceptance_info/',
                self.admin_site.admin_view(self.provider_acceptance_info_view),
                name='provider_acceptance_info',
            ),
            path(
                '<int:booking_id>/client_acceptance_info/',
                self.admin_site.admin_view(self.client_acceptance_info_view),
                name='client_acceptance_info',
            ),
        ]
        return custom_urls + urls

    def provider_acceptance_info_view(self, request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        context = dict(
            self.admin_site.each_context(request),
            title=f"Provider Acceptance Details – {booking.booking_number}",
            booking=booking,
            fields={
                "Accepted Terms": "✅ Yes" if booking.provider_accepted_terms else "❌ No",
                "Acceptance Date/Time": booking.provider_acceptance_datetime.strftime("%d/%m/%Y %H:%M")
                if booking.provider_acceptance_datetime else "—",
                "IP Address": booking.provider_acceptance_ip or "—",
                "User Agent": booking.provider_acceptance_user_agent or "—",
                "Accepted Text": booking.provider_acceptance_text or "—",
            },
        )
        return TemplateResponse(request, "app/provider_acceptance_info.html", context)

    def client_acceptance_info_view(self, request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        context = dict(
            self.admin_site.each_context(request),
            title=f"Client Acceptance Details – {booking.booking_number}",
            booking=booking,
            fields={
                "Accepted Terms": "✅ Yes" if booking.client_accepted_terms else "❌ No",
                "Acceptance Date/Time": booking.client_acceptance_datetime.strftime("%d/%m/%Y %H:%M")
                if booking.client_acceptance_datetime else "—",
                "IP Address": booking.client_acceptance_ip or "—",
                "User Agent": booking.client_acceptance_user_agent or "—",
            },
        )
        return TemplateResponse(request, "app/client_acceptance_info.html", context)

    # ==========================
    # Columnas personalizadas
    # ==========================
    def status_colored(self, obj):
        # Color según el estado
        color = "orange"
        text = obj.status.capitalize()
        if obj.status == 'confirmed':
            color = "green"
        elif obj.status == 'cancelled':
            color = "red"

        # Fecha/hora en negro (provider_response_date)
        date_str = obj.provider_response_date.strftime('%d/%m/%Y %H:%M') if obj.provider_response_date else "—"

        return format_html(
            '<b><span style="color:{};">{}</span></b> <span style="color:black;">{}</span>',
            color, text, date_str
        )
    status_colored.short_description = 'Status'

    # Métodos originales de columnas
    def activity_date(self, obj):
        return obj.date.strftime('%d/%m/%Y') if obj.date else '—'
    activity_date.short_description = 'Date'

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

    def provider_accept_terms(self, obj):
        if obj.provider_accepted_terms:
            url = f"/admin/app/booking/{obj.id}/provider_acceptance_info/"
            return format_html(
                '<a class="button" style="background-color:#28a745;color:white;padding:3px 6px;border-radius:4px;text-decoration:none;" href="{}">✅ Accepted</a>', url
            )
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')
    provider_accept_terms.short_description = "Provider Accepted Terms"

    def client_accept_terms(self, obj):
        if obj.client_accepted_terms:
            url = f"/admin/app/booking/{obj.id}/client_acceptance_info/"
            return format_html(
                '<a class="button" style="background-color:#007bff;color:white;padding:3px 6px;border-radius:4px;text-decoration:none;" href="{}">✅ Accepted</a>',
                url
            )
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')
    client_accept_terms.short_description = "Client Accepted Terms"

    def price(self, obj):
        if obj.safari and obj.safari.provider_price:
            return f"{obj.safari.provider_price:.2f}"
        return "—"
    price.short_description = 'Pro Price pp'

    def provider_earnings(self, obj):
        if obj.safari and obj.safari.provider_price:
            amount = obj.safari.provider_price * obj.number_of_people
            return format_html('<span style="color: black;">{}</span>', f"{amount:.2f}")
        return "—"
    provider_earnings.short_description = 'Pro Price tot'

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
    client_payment.short_description = 'Client Price tot'

    def client_unit_price(self, obj):
        if obj.safari and obj.safari.client_price:
            return f"{obj.safari.client_price:.2f}"
        return "—"
    client_unit_price.short_description = 'Client Price pp'

    def client_name(self, obj):
        return obj.client_name if obj.client_name else '—'
    client_name.short_description = 'Client'

    def client_email(self, obj):
        return obj.client_email if obj.client_email else '—'
    client_email.short_description = 'Email'

    def formatted_client_phone(self, obj):
        if obj.client_phone_prefix and obj.client_phone_number:
            return f"{obj.client_phone_prefix} {obj.client_phone_number}"
        return "—"
    formatted_client_phone.short_description = 'Phone'

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset |= self.model.objects.annotate(
                full_phone=Concat('client_phone_prefix', Value(' '), 'client_phone_number')
            ).filter(full_phone__icontains=search_term)
        return queryset, use_distinct

    class Media:
        css = {'all': ('app/css/admin_custom.css?v=2.1',)}
        js = ('app/js/admin_custom.js?v=2.1',)

# ===============================
# Otros modelos
# ===============================
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
