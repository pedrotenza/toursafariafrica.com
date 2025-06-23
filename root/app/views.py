from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Safari, Booking, HomePage
import smtplib
from email.mime.text import MIMEText


def home(request):
    homepage = HomePage.objects.first()
    return render(request, 'app/home.html', {'homepage': homepage})


def safari_list(request):
    safaris = Safari.objects.all()
    return render(request, 'app/safari_list.html', {'safaris': safaris})


def safari_detail(request, safari_id):
    safari = get_object_or_404(Safari, pk=safari_id)

    highlight_lines = safari.highlights.split('.') if safari.highlights else []
    highlight_lines = [line.strip() for line in highlight_lines if line.strip()]

    error_message = None  # Para mostrar errores en el template

    if request.method == 'POST':
        print("✅ Form received via POST")
        try:
            name = request.POST['name']
            email = request.POST['email']
            phone = request.POST.get('phone', '')
            nationality = request.POST.get('nationality', '')
            age = int(request.POST.get('age', 0))
            date = request.POST['date']
            number_of_people = int(request.POST.get('number_of_people', 1))  

            # Validar contra min/max del safari
            if safari.min_people and number_of_people < safari.min_people:
                error_message = f"Minimum number of people is {safari.min_people}."
            elif safari.max_people and number_of_people > safari.max_people:
                error_message = f"Maximum number of people is {safari.max_people}."

            if error_message:
                # Mostrar el error en el formulario sin perder datos
                return render(request, 'app/safari_detail.html', {
                    'safari': safari,
                    'highlight_lines': highlight_lines,
                    'error_message': error_message
                })

            print(f"Received data: {name}, {email}, {phone}, {nationality}, {age}, {date}, {number_of_people}")

            booking = Booking.objects.create(
                safari=safari,
                client_name=name,
                client_email=email,
                client_phone=phone,
                client_nationality=nationality,
                client_age=age,
                date=date,
                number_of_people=number_of_people
            )
            print("🟢 Booking saved successfully")

            provider_email = safari.provider.email if safari.provider else None

            site_url = request.build_absolute_uri('/')[:-1]
            confirm_url = f"{site_url}/booking/confirm/{booking.id}/"
            cancel_url = f"{site_url}/booking/cancel/{booking.id}/"

            # Enviar correo al cliente
            try:
                ----
                sender = "pedro.tenza@outlook.com"
                recipient = email

                client_body = f"""
Hello {name},

Thank you for booking the safari: {safari.name}
Selected date: {date}
Number of people: {number_of_people}

Please note that your booking must be confirmed by the safari provider.  
We will contact you soon with the confirmation and further details.

Best regards,  
The Safari Team
"""
                message = MIMEText(client_body)
                message["Subject"] = "Safari Booking Request"
                message["From"] = sender
                message["To"] = recipient

                server = smtplib.SMTP("smtp.sendgrid.net", 587)
                server.starttls()
                server.login("apikey", api_key)
                server.sendmail(sender, recipient, message.as_string())
                print("✅ Email sent to client.")
                
                # Email al proveedor
                if provider_email:
                    provider_body = f"""
Hola {safari.provider.name},

Se ha realizado una nueva solicitud de reserva para el safari: {safari.name}  
Fecha seleccionada: {date}  
Participantes: {number_of_people}
Nombre del cliente: {name}  
Email del cliente: {email}  
Teléfono del cliente: {phone}  
Nacionalidad del cliente: {nationality}  
Edad del cliente: {age}

Para CONFIRMAR la reserva, haz clic en este enlace:
{confirm_url}

Para CANCELAR la reserva, haz clic en este enlace:
{cancel_url}

Gracias,  
El equipo de Safaris
"""
                    provider_message = MIMEText(provider_body)
                    provider_message["Subject"] = "Nueva solicitud de reserva de safari"
                    provider_message["From"] = sender
                    provider_message["To"] = provider_email

                    server.sendmail(sender, provider_email, provider_message.as_string())
                    print("📩 Email enviado al proveedor.")

                server.quit()
            except Exception as e:
                print("❌ Error sending email:", e)

        except Exception as e:
            print("❌ Error saving the booking:", e)

        return redirect('safari_list')

    return render(request, 'app/safari_detail.html', {
        'safari': safari,
        'highlight_lines': highlight_lines
    })


def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.confirmed_by_provider = True
    booking.save()
    return HttpResponse("✅ Reserva confirmada correctamente.")


def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return HttpResponse("❌ Reserva cancelada correctamente.")
