from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Safari, Booking, HomePage
import smtplib
from email.mime.text import MIMEText


def home(request):
    homepage = HomePage.objects.first()  # Assuming there is only one entry
    return render(request, 'app/home.html', {'homepage': homepage})


def safari_list(request):
    safaris = Safari.objects.all()
    return render(request, 'app/safari_list.html', {'safaris': safaris})


def safari_detail(request, safari_id):
    safari = get_object_or_404(Safari, pk=safari_id)

    highlight_lines = safari.highlights.split('.') if safari.highlights else []
    highlight_lines = [line.strip() for line in highlight_lines if line.strip()]

    if request.method == 'POST':
        print("✅ Form received via POST")
        try:
            name = request.POST['name']
            email = request.POST['email']
            phone = request.POST.get('phone', '')  # Opcional
            nationality = request.POST.get('nationality', '')  # Opcional
            age = int(request.POST.get('age', 0))  # Si no viene, 0 o puedes manejar error
            date = request.POST['date']
            print(f"Received data: {name}, {email}, {phone}, {nationality}, {age}, {date}")

            booking = Booking.objects.create(
                safari=safari,
                client_name=name,
                client_email=email,
                client_phone=phone,
                client_nationality=nationality,
                client_age=age,
                date=date
            )
            print("🟢 Booking saved successfully")

            # Datos del proveedor
            provider_email = safari.provider.email if safari.provider else None

            # Enlaces públicos de confirmación/cancelación
            site_url = request.build_absolute_uri('/')[:-1]
            confirm_url = f"{site_url}/booking/confirm/{booking.id}/"
            cancel_url = f"{site_url}/booking/cancel/{booking.id}/"

            # Enviar correo al cliente
            try:
                ------------------------------------
                sender = "pedro.tenza@outlook.com"
                recipient = email  # To the client who booked

                client_body = f"""
Hello {name},

Thank you for booking the safari: {safari.name}
Selected date: {date}

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
                
                # Enviar correo al proveedor
                if provider_email:
                    provider_body = f"""
Hola {safari.provider.name},

Se ha realizado una nueva solicitud de reserva para el safari: {safari.name}  
Fecha seleccionada: {date}  
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