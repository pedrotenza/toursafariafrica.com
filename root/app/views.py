from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from .models import Safari, Booking, HomePage, Participant
from .services.booking_service import create_booking, confirm_booking_service, cancel_booking_service
from .forms import BookingForm, ParticipantFormSet


def get_client_ip(request):
    """
    Utility to obtain client's IP, supports X-Forwarded-For if behind proxy.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def home(request):
    homepage = HomePage.objects.first()
    return render(request, 'app/home.html', {'homepage': homepage})


def safari_list(request):
    safaris = Safari.objects.all()
    return render(request, 'app/safari_list.html', {'safaris': safaris})


def safari_detail(request, safari_id):
    safari = get_object_or_404(Safari, pk=safari_id)
    highlight_lines = [line.strip() for line in (safari.highlights.split('.') if safari.highlights else []) if line.strip()]
    error_message = None

    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['client_phone_prefix'] = post_data.get('client_phone_prefix', '')
        post_data['client_phone_number'] = post_data.get('client_phone_number', '')

        # ✅ Verificar aceptación de términos del cliente
        accept_terms = post_data.get('accept_terms')
        if not accept_terms:
            messages.error(request, "Debes aceptar los términos y condiciones antes de realizar la reserva.")
            return render(request, 'app/safari_detail.html', {
                'safari': safari,
                'highlight_lines': highlight_lines,
                'error_message': "Debes aceptar los términos y condiciones antes de continuar.",
                'price_per_person': safari.client_price,
                'client_terms_url': reverse('client_terms')
            })

        # Crear la reserva usando el servicio
        booking, error_message = create_booking(post_data, safari, request)
        if error_message:
            return render(request, 'app/safari_detail.html', {
                'safari': safari,
                'highlight_lines': highlight_lines,
                'error_message': error_message,
                'price_per_person': safari.client_price,
                'client_terms_url': reverse('client_terms')
            })

        # ✅ Registrar aceptación legal del cliente
        booking.client_accepted_terms = True
        booking.client_acceptance_datetime = timezone.now()
        booking.client_acceptance_ip = get_client_ip(request)
        booking.client_acceptance_user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        booking.client_acceptance_text = (
            "I have read and accept the Terms and Conditions as the client, "
            "and I hereby acknowledge and assume all legal responsibility and liabilities derived from my participation."
        )
        booking.save()

        client_email = booking.client_email if booking else "the client"
        messages.success(
            request,
            f"Booking request number {booking.booking_number} created successfully! Your reservation is pending confirmation by the provider.\n"
            "\n"
            "No payment will be processed until the provider confirms your booking.\n"
            "\n"
            f"An email with all the booking details has been sent to {client_email}."
        )

    return render(request, 'app/safari_detail.html', {
        'safari': safari,
        'highlight_lines': highlight_lines,
        'error_message': error_message,
        'price_per_person': safari.client_price,
        'client_terms_url': reverse('client_terms')
    })


# -------------------------------
# VISTA DE TÉRMINOS DEL CLIENTE
# -------------------------------
def client_terms_view(request):
    return render(request, 'app/client_terms_and_conditions.html')


# -------------------------------
# VISTA DE TÉRMINOS DEL PROVEEDOR
# -------------------------------
def provider_terms_view(request, booking_id=None):
    booking = None
    if booking_id:
        booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'app/provider_terms_and_conditions.html', {'booking': booking})


# -------------------------------
# CONFIRMACIÓN DE RESERVA (Proveedor)
# -------------------------------
def booking_confirmed(request, booking_number):
    booking = get_object_or_404(Booking, booking_number=booking_number)
    participants = Participant.objects.filter(booking=booking)

    total_client_amount = booking.safari.client_price * booking.number_of_people
    total_provider_amount = booking.safari.provider_price * booking.number_of_people
    is_provider_view = request.GET.get('provider', False) or not request.user.is_authenticated

    # Redirecciones según estado actual
    if booking.status == 'cancelled':
        messages.info(request, "Esta reserva ha sido cancelada.")
        return redirect('booking_cancelled', booking_number=booking.booking_number)
    elif booking.status == 'confirmed':
        messages.info(request, "Esta reserva ya ha sido confirmada.")

    if request.method == 'POST':
        action = request.POST.get('action')

        # -------------------
        # Confirmación
        # -------------------
        if action == 'confirm' and booking.status == 'pending':
            accept_terms = request.POST.get('accept_terms')
            if not accept_terms:
                messages.error(request, "Debes aceptar los términos y condiciones para confirmar la reserva.")
                return redirect('booking_confirmed', booking_number=booking_number)

            booking.provider_accepted_terms = True
            booking.provider_acceptance_datetime = timezone.now()
            booking.provider_acceptance_ip = get_client_ip(request)
            booking.provider_acceptance_user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            booking.provider_acceptance_text = (
                "I have read and accept the Terms and Conditions, and as the provider, "
                "I hereby acknowledge and assume all legal responsibility and liabilities."
            )
            booking.confirmed_by_provider = True
            booking.provider_response_date = timezone.now()
            booking.status = 'confirmed'
            booking.save()

            html_result = confirm_booking_service(booking.id, request)
            if "✅" in html_result:
                messages.success(request, "✅ Reserva confirmada correctamente.")
            else:
                messages.error(request, "❌ Error al confirmar la reserva.")

        # -------------------
        # Cancelación
        # -------------------
        elif action == 'cancel' and booking.status == 'pending':
            booking.status = 'cancelled'
            booking.save()

            html_result = cancel_booking_service(booking.id)
            if "❌ Booking canceled successfully" in html_result:
                messages.success(request, "❌ Reserva cancelada correctamente.")
            else:
                messages.error(request, "❌ Error al cancelar la reserva.")

        return redirect('booking_confirmed', booking_number=booking_number)

    context = {
        'booking': booking,
        'participants': participants,
        'total_client_amount': total_client_amount,
        'total_provider_amount': total_provider_amount,
        'is_provider_view': is_provider_view,
        'provider_terms_url': reverse('provider_terms', args=[booking.id])
    }

    return render(request, 'app/booking_confirmed.html', context)


# -------------------------------
# Confirmación individual (POST)
# -------------------------------
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    participants = Participant.objects.filter(booking=booking)
    total_provider_amount = booking.safari.provider_price * booking.number_of_people

    if booking.status != 'pending':
        if booking.status == 'confirmed':
            messages.info(request, "Esta reserva ya ha sido confirmada.")
        else:
            messages.info(request, "Esta reserva ha sido cancelada.")
        return redirect('booking_confirmed', booking_number=booking.booking_number)

    if request.method == 'POST':
        accept_terms = request.POST.get('accept_terms')
        if not accept_terms:
            messages.error(request, "Debes aceptar los términos y condiciones para confirmar la reserva.")
            return redirect('booking_confirmed', booking_number=booking.booking_number)

        booking.provider_accepted_terms = True
        booking.provider_acceptance_datetime = timezone.now()
        booking.provider_acceptance_ip = get_client_ip(request)
        booking.provider_acceptance_user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        booking.provider_acceptance_text = (
            "I have read and accept the Terms and Conditions, and as the provider, "
            "I hereby acknowledge and assume all legal responsibility and liabilities."
        )
        booking.confirmed_by_provider = True
        booking.provider_response_date = timezone.now()
        booking.status = 'confirmed'
        booking.save()

        html_result = confirm_booking_service(booking_id, request)
        if "✅" in html_result:
            messages.success(request, "Reserva confirmada correctamente.")
        else:
            messages.error(request, "No se pudo confirmar la reserva.")

        return redirect('booking_confirmed', booking_number=booking.booking_number)

    return render(request, 'app/confirm_booking.html', {
        'booking': booking,
        'participants': participants,
        'provider_terms_url': reverse('provider_terms', args=[booking.id]),
        'total_provider_amount': total_provider_amount
    })


# -------------------------------
# Cancelación de reserva (POST)
# -------------------------------
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    participants = Participant.objects.filter(booking=booking)

    if booking.status != 'pending':
        if booking.status == 'cancelled':
            messages.info(request, "Esta reserva ya ha sido cancelada.")
            return redirect('booking_cancelled', booking_number=booking.booking_number)
        else:
            messages.info(request, "Esta reserva ya ha sido confirmada y no puede cancelarse aquí.")
            return redirect('booking_confirmed', booking_number=booking.booking_number)

    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()

        html_result = cancel_booking_service(booking_id)
        if "❌ Booking canceled successfully" in html_result:
            messages.success(request, "Reserva cancelada correctamente.")
        else:
            messages.error(request, "No se pudo cancelar la reserva.")
        return redirect('booking_cancelled', booking_number=booking.booking_number)

    return render(request, 'app/cancel_booking.html', {
        'booking': booking,
        'participants': participants,
    })


def booking_cancelled(request, booking_number):
    booking = get_object_or_404(Booking, booking_number=booking_number)
    participants = Participant.objects.filter(booking=booking)

    context = {
        'booking': booking,
        'participants': participants,
    }

    return render(request, 'app/booking_cancelled.html', context)


class BookingCreateView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'app/booking_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participant_formset'] = ParticipantFormSet(self.request.POST or None)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        participant_formset = context['participant_formset']

        if participant_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.client_phone_prefix = form.cleaned_data.get('client_phone_prefix', '')
            self.object.client_phone_number = form.cleaned_data.get('client_phone_number', '')
            self.object.save()

            participant_formset.instance = self.object
            participant_formset.save()

            client_email = self.object.client_email if self.object.client_email else "the client"
            messages.success(
                self.request,
                "✅ Booking created successfully! Your reservation is pending confirmation by the provider.\n"
                "\n"
                "No payment will be processed until the provider confirms your booking.\n"
                "\n"
                f"An email with all the booking information has been sent to {client_email}."
            )

            return super().form_valid(form)
        else:
            return self.form_invalid(form)


def booking_debug(request, booking_number):
    booking = get_object_or_404(Booking, booking_number=booking_number)
    participants = Participant.objects.filter(booking=booking)

    debug_info = {
        'booking_exists': True,
        'booking_id': booking.id,
        'booking_number': booking.booking_number,
        'participants_count': participants.count(),
        'participants_list': list(participants.values('id', 'age', 'nationality')),
        'has_participants_attr': hasattr(booking, 'participants'),
    }

    return render(request, 'app/booking_debug.html', {
        'booking': booking,
        'participants': participants,
        'debug_info': debug_info
    })
