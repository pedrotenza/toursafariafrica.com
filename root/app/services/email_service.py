import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from .invoice_service import generate_invoice_pdf
import os
from dotenv import load_dotenv
from django.urls import reverse

load_dotenv()

SMTP_USER = os.getenv('BREVO_SMTP_USER')
SMTP_PASSWORD = os.getenv('BREVO_SMTP_PASSWORD')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')


def request_build_url(request, path_name, booking_id):
    relative_url = reverse(path_name, args=[booking_id])
    return request.build_absolute_uri(relative_url)


def send_booking_request_email(booking, request):
    try:
        sender = SENDER_EMAIL
        recipient = booking.client_email
        subject = f"{booking.safari.name} – Booking Request with TourSafariAfrica – {booking.date.strftime('%d.%m.%Y')}"

        client_body = f"""
        <html>
          <body>
            <p>Dear {booking.client_name},</p>
            <p>Thank you for your booking request for the activity:</p>
            <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
            <pre>
Selected Date:        {booking.date.strftime("%d-%m-%Y")}
Price per Person:     {booking.safari.client_price:.2f}
Participants:         {booking.number_of_people}
-------------------------------
Total Price:          {booking.safari.client_price * booking.number_of_people:.2f}
            </pre>
            <p>Please note that your booking must be confirmed by the provider.</p>
            <p>We will contact you soon with the confirmation and further details.</p>
            <p>Best regards,<br>The TourSafariAfrica Team</p>
          </body>
        </html>
        """

        message = MIMEText(client_body, "html")
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = recipient

        server = smtplib.SMTP("smtp-relay.brevo.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(sender, recipient, message.as_string())
        print("✅ Booking request email sent to client.")

        if booking.safari.provider and booking.safari.provider.email:
            provider_email = booking.safari.provider.email
            total_provider_price = booking.safari.provider_price * booking.number_of_people

            confirm_url = request_build_url(request, 'confirm_booking', booking.id)
            cancel_url = request_build_url(request, 'cancel_booking', booking.id)

            provider_body = f"""
            <html>
              <body>
                <p>Hello {booking.safari.provider.name},</p>
                <p>A new booking request has been made for the safari:</p>
                <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
                <pre>
Selected Date:             {booking.date.strftime("%d-%m-%Y")}
Price per Person:          {booking.safari.provider_price:.2f}
Number of Participants:    {booking.number_of_people}
---------------------------------------------
Amount to Be Paid to You:  {total_provider_price:.2f}
                </pre>
                <p>Client Details:</p>
                <pre>
Name:        {booking.client_name}
Age:         {booking.client_age}
Nationality: {booking.client_nationality}
                </pre>
                <p>To <strong>CONFIRM</strong> the booking, click here:<br>
                <a href="{confirm_url}">{confirm_url}</a></p>
                <p>To <strong>CANCEL</strong> the booking, click here:<br>
                <a href="{cancel_url}">{cancel_url}</a></p>
                <p>Best regards,<br>The TourSafariAfrica Team</p>
              </body>
            </html>
            """

            provider_message = MIMEMultipart()
            provider_message['Subject'] = subject
            provider_message['From'] = sender
            provider_message['To'] = provider_email
            provider_message.attach(MIMEText(provider_body, "html"))

            server.sendmail(sender, provider_email, provider_message.as_string())
            print("📩 Booking request email sent to provider.")

        server.quit()

    except Exception as e:
        print(f"❌ Error sending booking request emails: {e}")


def send_booking_confirmation_emails(booking, request):
    try:
        sender = SENDER_EMAIL

        client_subject = f"{booking.safari.name} – Booking Confirmed – {booking.date.strftime('%d.%m.%Y')}"
        client_body = f"""
        <html>
          <body>
            <p>Dear {booking.client_name},</p>
            <p>Your booking has been confirmed.</p>
            <h3>Booking Details:</h3>
            <pre>
Activity: {booking.safari.name}
Date: {booking.date.strftime("%d-%m-%Y")}
Participants: {booking.number_of_people}
Total Price: ${booking.safari.client_price * booking.number_of_people:.2f}
            </pre>
            <p>You will find your invoice attached to this email.</p>
            <p>Thank you for choosing TourSafariAfrica!</p>
            <p>Best regards,<br>The TourSafariAfrica Team</p>
          </body>
        </html>
        """
        invoice_client = generate_invoice_pdf(booking, for_provider=False)

        message_client = MIMEMultipart()
        message_client["Subject"] = client_subject
        message_client["From"] = sender
        message_client["To"] = booking.client_email
        message_client.attach(MIMEText(client_body, "html"))

        part_client = MIMEApplication(invoice_client, Name="Invoice_Client.pdf")
        part_client['Content-Disposition'] = 'attachment; filename="Invoice_Client.pdf"'
        message_client.attach(part_client)

        server = smtplib.SMTP("smtp-relay.brevo.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(sender, booking.client_email, message_client.as_string())
        print("✅ Confirmation email sent to client.")

        if booking.safari.provider and booking.safari.provider.email:
            provider_subject = f"{booking.safari.name} – Booking Confirmed – {booking.date.strftime('%d.%m.%Y')}"
            provider_body = f"""
            <html>
              <body>
                <p>Hello {booking.safari.provider.name},</p>
                <p>Thank you for confirming the booking request!</p>
                <h3>Booking Details:</h3>
                <pre>
Activity: {booking.safari.name}
Date: {booking.date.strftime("%d-%m-%Y")}
Participants: {booking.number_of_people}
Amount to Receive: ${booking.safari.provider_price * booking.number_of_people:.2f}
                </pre>
                <p>Client:</p>
                <pre>
Name: {booking.client_name}
Email: {booking.client_email}
Phone: {booking.client_phone}
                </pre>
                <p>You will find your invoice attached to this email.</p>
                <p>Best regards,<br>The TourSafariAfrica Team</p>
              </body>
            </html>
            """
            invoice_provider = generate_invoice_pdf(booking, for_provider=True)

            provider_message = MIMEMultipart()
            provider_message["Subject"] = provider_subject
            provider_message["From"] = sender
            provider_message["To"] = booking.safari.provider.email
            provider_message.attach(MIMEText(provider_body, "html"))

            part_provider = MIMEApplication(invoice_provider, Name="Invoice_Provider.pdf")
            part_provider['Content-Disposition'] = 'attachment; filename="Invoice_Provider.pdf"'
            provider_message.attach(part_provider)

            server.sendmail(sender, booking.safari.provider.email, provider_message.as_string())
            print("✅ Confirmation email sent to provider.")

        server.quit()

    except Exception as e:
        print(f"❌ Error sending confirmation emails: {e}")


def send_booking_cancellation_emails(booking):
    try:
        sender = SENDER_EMAIL
        server = smtplib.SMTP("smtp-relay.brevo.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)

        subject = f"{booking.safari.name} – Booking Canceled – {booking.date.strftime('%d.%m.%Y')}"

        # Cliente
        client_body = f"""
        <html><body>
            <p>Dear {booking.client_name},</p>
            <p>Your booking for <strong>{booking.safari.name}</strong> on {booking.date.strftime('%d‑%m‑%Y')} has been canceled.</p>
            <p>If you had already paid, the full amount has been refunded.</p>
            <p>Attached is your cancellation receipt.</p>
            <p>Best regards,<br>TourSafariAfrica Team</p>
        </body></html>
        """
        msg_client = MIMEMultipart()
        msg_client["Subject"] = subject
        msg_client["From"] = sender
        msg_client["To"] = booking.client_email
        msg_client.attach(MIMEText(client_body, "html"))
        invoice_pdf = generate_invoice_pdf(booking, for_provider=False)
        part_cli = MIMEApplication(invoice_pdf, Name="Cancellation_Receipt_Client.pdf")
        part_cli["Content-Disposition"] = 'attachment; filename="Cancellation_Receipt_Client.pdf"'
        msg_client.attach(part_cli)
        server.sendmail(sender, booking.client_email, msg_client.as_string())
        print("📧 Cancellation email + receipt sent to client.")

        # Proveedor
        if booking.safari.provider and booking.safari.provider.email:
            provider_body = f"""
            <html><body>
                <p>Hello {booking.safari.provider.name},</p>
                <p>The booking for <strong>{booking.safari.name}</strong> on {booking.date.strftime('%d‑%m‑%Y')} has been canceled.</p>
                <p>Attached is a copy of the cancellation receipt.</p>
            </body></html>
            """
            msg_prov = MIMEMultipart()
            msg_prov["Subject"] = subject
            msg_prov["From"] = sender
            msg_prov["To"] = booking.safari.provider.email
            msg_prov.attach(MIMEText(provider_body, "html"))
            invoice_pdf_prov = generate_invoice_pdf(booking, for_provider=True)
            part_prv = MIMEApplication(invoice_pdf_prov, Name="Cancellation_Receipt_Provider.pdf")
            part_prv["Content-Disposition"] = 'attachment; filename="Cancellation_Receipt_Provider.pdf"'
            msg_prov.attach(part_prv)
            server.sendmail(sender, booking.safari.provider.email, msg_prov.as_string())
            print("📧 Cancellation email + receipt sent to provider.")

        server.quit()

    except Exception as e:
        print(f"❌ Error sending cancellation emails: {e}")
