from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import CreateView
from .models import Safari, Booking, HomePage
from .services.booking_service import create_booking, confirm_booking_service, cancel_booking_service
from .forms import BookingForm, ParticipantFormSet


def home(request):
    """Vista de la página principal."""
    homepage = HomePage.objects.first()
    return render(request, 'app/home.html', {'homepage': homepage})


def safari_list(request):
    """Lista de todos los safaris disponibles."""
    safaris = Safari.objects.all()
    return render(request, 'app/safari_list.html', {'safaris': safaris})


def safari_detail(request, safari_id):
    """Detalle de un safari y creación de reserva."""
    activity = get_object_or_404(Safari, pk=safari_id)
    highlight_lines = activity.highlights.split('.') if activity.highlights else []
    highlight_lines = [line.strip() for line in highlight_lines if line.strip()]
    error_message = None

    if request.method == 'POST':
        post_data = request.POST.copy()
        # Asegurar que existan los campos de teléfono
        post_data['client_phone_prefix'] = post_data.get('client_phone_prefix', '')
        post_data['client_phone_number'] = post_data.get('client_phone_number', '')

        booking, error_message = create_booking(post_data, activity, request)
        if error_message:
            return render(request, 'app/safari_detail.html', {
                'safari': activity,
                'highlight_lines': highlight_lines,
                'error_message': error_message,
                'price_per_person': activity.client_price,
            })
        return redirect('safari_list')

    return render(request, 'app/safari_detail.html', {
        'safari': activity,
        'highlight_lines': highlight_lines,
        'error_message': error_message,
        'price_per_person': activity.client_price,
    })


def confirm_booking(request, booking_id):
    """Confirmar una reserva a través del servicio."""
    response = confirm_booking_service(booking_id, request)
    return HttpResponse(response)


def cancel_booking(request, booking_id):
    """Cancelar una reserva a través del servicio."""
    response = cancel_booking_service(booking_id)
    return HttpResponse(response)


class BookingCreateView(CreateView):
    """Vista genérica para crear una reserva con participantes."""
    model = Booking
    form_class = BookingForm
    template_name = 'app/booking_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['participant_formset'] = ParticipantFormSet(self.request.POST)
        else:
            context['participant_formset'] = ParticipantFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        participant_formset = context['participant_formset']

        if participant_formset.is_valid():
            # Guardar booking con los campos correctos de teléfono
            self.object = form.save(commit=False)
            self.object.client_phone_prefix = form.cleaned_data.get('client_phone_prefix', '')
            self.object.client_phone_number = form.cleaned_data.get('client_phone_number', '')
            self.object.save()

            # Guardar participantes relacionados
            participant_formset.instance = self.object
            participant_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
