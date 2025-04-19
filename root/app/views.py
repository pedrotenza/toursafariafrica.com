from django.shortcuts import render, get_object_or_404, redirect
from .models import Safari, Booking

# Vista para la página de inicio
def home(request):
    return render(request, 'app/home.html')  # Asegúrate de tener este archivo 'home.html' en el directorio correcto

# Vista para la lista de safaris
def safari_list(request):
    safaris = Safari.objects.all()  # Obtén todos los safaris de la base de datos
    return render(request, 'app/safari_list.html', {'safaris': safaris})

# Vista para los detalles de un safari en particular
def safari_detail(request, safari_id):
    safari = get_object_or_404(Safari, pk=safari_id)  # Obtiene el safari por su id o muestra un 404 si no lo encuentra
    if request.method == 'POST':
        # Si es un POST, crea una nueva reserva para el safari
        name = request.POST['name']
        email = request.POST['email']
        date = request.POST['date']
        Booking.objects.create(
            safari=safari,
            client_name=name,
            client_email=email,
            date=date
        )
        return redirect('safari_list')  # Después de guardar la reserva, redirige a la lista de safaris
    return render(request, 'app/safari_detail.html', {'safari': safari})
