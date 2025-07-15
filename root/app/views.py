from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import CreateView
from .models import Safari, Booking, HomePage
from .services.booking_service import create_booking, confirm_booking_service, cancel_booking_service
from .forms import BookingForm, ParticipantFormSet

def home(request):
    homepage = HomePage.objects.first()
    return render(request, 'app/home.html', {'homepage': homepage})

def safari_list(request):
    safaris = Safari.objects.all()
    return render(request, 'app/safari_list.html', {'safaris': safaris})

def safari_detail(request, safari_id):
    activity = get_object_or_404(Safari, pk=safari_id)
    highlight_lines = activity.highlights.split('.') if activity.highlights else []
    highlight_lines = [line.strip() for line in highlight_lines if line.strip()]
    error_message = None

    if request.method == 'POST':
        booking, error_message = create_booking(request.POST, activity, request)
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
    response = confirm_booking_service(booking_id, request)
    return HttpResponse(response)

def cancel_booking(request, booking_id):
    response = cancel_booking_service(booking_id)
    return HttpResponse(response)

class BookingCreateView(CreateView):
    model = Booking
    form_class = BookingForm

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
            self.object = form.save()
            participant_formset.instance = self.object
            participant_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)