from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.mail import EmailMessage
from .models import Safari, Booking, HomePage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import os
from django.conf import settings
import uuid
from io import BytesIO
from reportlab.pdfgen import canvas

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
        print("✅ Form received via POST")
        try:
            name = request.POST['name']
            email = request.POST['email']
            phone = request.POST.get('phone', '')
            nationality = request.POST.get('nationality', '')
            age = int(request.POST.get('age', 0))

            date_str = request.POST['date']
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            number_of_people = int(request.POST.get('number_of_people', 1))

            if activity.min_people and number_of_people < activity.min_people:
                error_message = f"Minimum number of people is {activity.min_people}."
            elif activity.max_people and number_of_people > activity.max_people:
                error_message = f"Maximum number of people is {activity.max_people}."

            if error_message:
                return render(request, 'app/safari_detail.html', {
                    'safari': activity,
                    'highlight_lines': highlight_lines,
                    'error_message': error_message,
                    'price_per_person': activity.client_price,
                })

            booking = Booking.objects.create(
                safari=activity,
                client_name=name,
                client_email=email,
                client_phone=phone,
                client_nationality=nationality,
                client_age=age,
                date=date,
                number_of_people=number_of_people,
                payment_status='pending'  # Nuevo campo para el estado del pago
            )
            print("🟢 Booking saved successfully")

            provider_email = activity.provider.email if activity.provider else None
            site_url = request.build_absolute_uri('/')[:-1]
            confirm_url = f"{site_url}/booking/confirm/{booking.id}/"
            cancel_url = f"{site_url}/booking/cancel/{booking.id}/"

            try:
                ----
                sender = "pedro.tenza@outlook.com"
                recipient = email

                # --- Email to client (HTML) ---
                client_body = f"""
<html>
  <body>
    <p>Dear {name},<br><br>
    <p>Thank you for your booking request for the activity:</p>
    
    <p style="font-size: 20px; font-weight: bold;">{activity.name}</p>
    
    <pre>
Selected Date:        {date.strftime("%d-%m-%Y")}

Price per Person:     {activity.client_price:.2f}
Participants:         {number_of_people}
-------------------------------
Total Price:          {activity.client_price * number_of_people:.2f}
    </pre>

    <p>Please note that your booking must be confirmed by the provider.<br>
    
    <p>We will contact you soon with the confirmation and further details.<br><br>

    <p>Best regards,<br>The TourSafariAfrica Team</p>
  </body>
</html>
"""
                message = MIMEText(client_body, "html")
                message["Subject"] = f"{activity.name} – Booking Request with TourSafariAfrica – {date.strftime('%d.%m.%Y')}"
                message["From"] = sender
                message["To"] = recipient

                server = smtplib.SMTP("smtp.sendgrid.net", 587)
                server.starttls()
                server.login("apikey", api_key)
                server.sendmail(sender, recipient, message.as_string())
                print("✅ Email sent to client.")

                # --- Email to provider (HTML) ---
                if provider_email:
                    total_provider_price = activity.provider_price * number_of_people
                    provider_body = f"""
<html>
  <body>
    <p>Hello {activity.provider.name},<br><br>
    
    <p>A new booking request has been made for the safari:</p>

    <p style="font-size: 20px; font-weight: bold;">{activity.name}</p>

    <pre>
Selected Date:             {date.strftime("%d-%m-%Y")}

Price per Person:          {activity.provider_price:.2f}
Number of Participants:    {number_of_people}
---------------------------------------------
Amount to Be Paid to You:  {total_provider_price:.2f}
    </pre>

    <p>Client Details:</p>
    <pre>
Name:        {name}
Age:         {age}
Nationality: {nationality}
    </pre>

    <p>To <strong>CONFIRM</strong> the booking, click here:<br>
    <a href="{confirm_url}">{confirm_url}</a></p>

    <p>To <strong>CANCEL</strong> the booking, click here:<br>
    <a href="{cancel_url}">{cancel_url}</a></p>

    <p>Best regards,<br>
    The TourSafariAfrica Team</p>
  </body>
</html>
"""
                    provider_message = MIMEText(provider_body, "html")
                    provider_message["Subject"] = f"{activity.name} – Booking Request with TourSafariAfrica – {date.strftime('%d.%m.%Y')}"
                    provider_message["From"] = sender
                    provider_message["To"] = provider_email

                    server.sendmail(sender, provider_email, provider_message.as_string())
                    print("📩 Email sent to the provider.")

                server.quit()
            except Exception as e:
                print("❌ Error sending email:", e)

        except Exception as e:
            print("❌ Error saving the booking:", e)

        return redirect('safari_list')

    return render(request, 'app/safari_detail.html', {
        'safari': activity,
        'highlight_lines': highlight_lines,
        'error_message': error_message,
        'price_per_person': activity.client_price,
    })

def generate_invoice_pdf(booking, invoice_type="client"):
    """Genera un PDF de factura o albarán simulado"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Configuración del documento
    p.setTitle(f"Invoice #{booking.id}")
    p.setFont("Helvetica-Bold", 16)
    
    # Encabezado
    if invoice_type == "client":
        p.drawString(100, 800, f"TOURSAFARIAFRICA - INVOICE")
    else:
        p.drawString(100, 800, f"TOURSAFARIAFRICA - PAYMENT RECEIPT")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Booking ID: {booking.id}")
    p.drawString(100, 760, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Detalles del cliente/proveedor
    y_position = 720
    if invoice_type == "client":
        p.drawString(100, y_position, f"Client: {booking.client_name}")
        y_position -= 20
        p.drawString(100, y_position, f"Email: {booking.client_email}")
    else:
        p.drawString(100, y_position, f"Provider: {booking.safari.provider.name}")
        y_position -= 20
        p.drawString(100, y_position, f"Email: {booking.safari.provider.email}")
    
    # Detalles de la reserva
    y_position -= 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y_position, "Booking Details:")
    p.setFont("Helvetica", 12)
    
    y_position -= 20
    p.drawString(100, y_position, f"Activity: {booking.safari.name}")
    y_position -= 20
    p.drawString(100, y_position, f"Date: {booking.date.strftime('%d-%m-%Y')}")
    y_position -= 20
    p.drawString(100, y_position, f"Participants: {booking.number_of_people}")
    
    # Detalles de pago
    y_position -= 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y_position, "Payment Details:")
    p.setFont("Helvetica", 12)
    
    y_position -= 20
    if invoice_type == "client":
        price = booking.safari.client_price
        total = price * booking.number_of_people
        p.drawString(100, y_position, f"Price per person: ${price:.2f}")
        y_position -= 20
        p.drawString(100, y_position, f"Total: ${total:.2f}")
        y_position -= 20
        p.drawString(100, y_position, "Payment method: Simulated Payment (will be Stripe/PayPal)")
        y_position -= 20
        p.drawString(100, y_position, "Status: PAID")
    else:
        price = booking.safari.provider_price
        total = price * booking.number_of_people
        p.drawString(100, y_position, f"Price per person: ${price:.2f}")
        y_position -= 20
        p.drawString(100, y_position, f"Total: ${total:.2f}")
        y_position -= 20
        p.drawString(100, y_position, "Payment method: Bank Transfer (Simulated)")
        y_position -= 20
        p.drawString(100, y_position, "Status: TRANSFERRED")
    
    # Pie de página
    y_position -= 60
    p.setFont("Helvetica", 10)
    p.drawString(100, y_position, "This is a simulated document for development purposes.")
    y_position -= 15
    p.drawString(100, y_position, "Real payment system will be implemented with Stripe/PayPal.")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer

def send_booking_confirmation_emails(booking, request):
    """Envía los emails de confirmación con facturas adjuntas"""
    try:
        ------
        sender = "pedro.tenza@outlook.com"
        
        # --- Email al cliente ---
        client_subject = f"{booking.safari.name} – Booking Confirmed – {booking.date.strftime('%d.%m.%Y')}"
        
        client_body = f"""
<html>
  <body>
    <p>Dear {booking.client_name},</p>
    
    <p>We are pleased to inform you that your booking has been confirmed by the provider!</p>
    
    <h3>Booking Details:</h3>
    <pre>
Activity:          {booking.safari.name}
Date:              {booking.date.strftime('%d-%m-%Y')}
Participants:      {booking.number_of_people}
Price per Person:  ${booking.safari.client_price:.2f}
Total Paid:        ${booking.safari.client_price * booking.number_of_people:.2f}
    </pre>
    
    <p>Please find attached your invoice for this booking.</p>
    
    <p>If you have any questions, don't hesitate to contact us.</p>
    
    <p>Best regards,<br>The TourSafariAfrica Team</p>
  </body>
</html>
"""
        # Generar factura para el cliente
        client_invoice = generate_invoice_pdf(booking, "client")
        
        # Crear email para el cliente
        client_msg = MIMEMultipart()
        client_msg['Subject'] = client_subject
        client_msg['From'] = sender
        client_msg['To'] = booking.client_email
        client_msg.attach(MIMEText(client_body, "html"))
        
        # Adjuntar factura
        part = MIMEApplication(client_invoice.read(), Name=f"invoice_{booking.id}.pdf")
        part['Content-Disposition'] = f'attachment; filename="invoice_{booking.id}.pdf"'
        client_msg.attach(part)
        
        # --- Email al proveedor ---
        if booking.safari.provider and booking.safari.provider.email:
            provider_subject = f"{booking.safari.name} – Payment Sent – {booking.date.strftime('%d.%m.%Y')}"
            
            provider_body = f"""
<html>
  <body>
    <p>Hello {booking.safari.provider.name},</p>
    
    <p>We have processed the payment for the following booking:</p>
    
    <h3>Booking Details:</h3>
    <pre>
Activity:          {booking.safari.name}
Date:              {booking.date.strftime('%d-%m-%Y')}
Participants:      {booking.number_of_people}
Your Earnings:     ${booking.safari.provider_price * booking.number_of_people:.2f}
    </pre>
    
    <p>Please find attached the payment receipt.</p>
    
    <p>The funds should appear in your account within 3-5 business days.</p>
    
    <p>Best regards,<br>The TourSafariAfrica Team</p>
  </body>
</html>
"""
            # Generar albarán para el proveedor
            provider_receipt = generate_invoice_pdf(booking, "provider")
            
            # Crear email para el proveedor
            provider_msg = MIMEMultipart()
            provider_msg['Subject'] = provider_subject
            provider_msg['From'] = sender
            provider_msg['To'] = booking.safari.provider.email
            provider_msg.attach(MIMEText(provider_body, "html"))
            
            # Adjuntar albarán
            part = MIMEApplication(provider_receipt.read(), Name=f"payment_{booking.id}.pdf")
            part['Content-Disposition'] = f'attachment; filename="payment_{booking.id}.pdf"'
            provider_msg.attach(part)
        
        # Enviar emails
        server = smtplib.SMTP("smtp.sendgrid.net", 587)
        server.starttls()
        server.login("apikey", api_key)
        
        # Enviar al cliente
        server.sendmail(sender, booking.client_email, client_msg.as_string())
        print("✅ Confirmation email sent to client")
        
        # Enviar al proveedor si existe
        if booking.safari.provider and booking.safari.provider.email:
            server.sendmail(sender, booking.safari.provider.email, provider_msg.as_string())
            print("📩 Payment confirmation sent to provider")
        
        server.quit()
        
    except Exception as e:
        print(f"❌ Error sending confirmation emails: {e}")

def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Simular el proceso de pago
    print(f"💳 Simulating payment processing for booking {booking_id}")
    print(f"💰 Charging client ${booking.safari.client_price * booking.number_of_people:.2f}")
    print(f"💸 Transferring ${booking.safari.provider_price * booking.number_of_people:.2f} to provider")
    
    # Marcar como confirmado y pagado
    booking.confirmed_by_provider = True
    booking.payment_status = 'paid'
    booking.payment_date = datetime.now()
    booking.save()
    
    # Enviar emails de confirmación con facturas
    send_booking_confirmation_emails(booking, request)
    
    return HttpResponse("""
    <h1>✅ Booking confirmed successfully</h1>
    <p>The payment has been processed (simulated).</p>
    <p>Confirmation emails with invoices have been sent to both client and provider.</p>
    <p><a href="/">Return to home</a></p>
    """)

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Simular cancelación de pago si ya estaba pagado
    if booking.payment_status == 'paid':
        print(f"🔄 Simulating refund processing for booking {booking_id}")
        print(f"💸 Refunding ${booking.safari.client_price * booking.number_of_people:.2f} to client")
    
    booking.delete()
    
    return HttpResponse("""
    <h1>❌ Booking canceled successfully</h1>
    <p>Any simulated payments have been refunded.</p>
    <p><a href="/">Return to home</a></p>
    """)