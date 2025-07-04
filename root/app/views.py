from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Safari, Booking, HomePage
from .services.booking_service import create_booking, confirm_booking_service, cancel_booking_service

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
