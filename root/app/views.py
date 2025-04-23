from django.shortcuts import render, get_object_or_404, redirect
from .models import Safari, Booking




from .models import HomePage

def home(request):
    homepage = HomePage.objects.first()  # Se asume que solo hay una entrada
    return render(request, 'app/home.html', {'homepage': homepage})


"""
# Vista para la página de inicio
def home(request):
    return render(request, 'app/home.html')
""" 

# Vista para la lista de safaris
def safari_list(request):
    safaris = Safari.objects.all()
    return render(request, 'app/safari_list.html', {'safaris': safaris})

# Vista para los detalles de un safari en particular
def safari_detail(request, safari_id):
    safari = get_object_or_404(Safari, pk=safari_id)

    # Extraer y formatear los puntos destacados para cada uno en una nueva línea
    highlight_lines = safari.highlights.split('.') if safari.highlights else []
    highlight_lines = [line.strip() for line in highlight_lines if line.strip()]

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

    return render(request, 'app/safari_detail.html', {
        'safari': safari,
        'highlight_lines': highlight_lines
    })
