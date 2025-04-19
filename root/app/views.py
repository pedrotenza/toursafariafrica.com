
from django.shortcuts import render, get_object_or_404, redirect
from .models import Safari, Booking

def safari_list(request):
    safaris = Safari.objects.all()
    return render(request, 'app/safari_list.html', {'safaris': safaris})

def safari_detail(request, safari_id):
    safari = get_object_or_404(Safari, pk=safari_id)
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        date = request.POST['date']
        Booking.objects.create(
            safari=safari,
            client_name=name,
            client_email=email,
            date=date
        )
        return redirect('safari_list')
    return render(request, 'app/safari_detail.html', {'safari': safari})
    
    