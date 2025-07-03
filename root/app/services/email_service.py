import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from .invoice_service import generate_invoice_pdf
import os
from dotenv import load_dotenv

# Cargar variables (redundante pero seguro)
load_dotenv()  # Esto asegura que funcione incluso si se ejecuta el módulo directamente



SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')

def send_booking_request_email(booking):
    try:
        sender = SENDER_EMAIL
        recipient = booking.client_email
        subject = f"{booking.safari.name} – Booking Request with TourSafariAfrica – {booking.date.strftime('%d.%m.%Y')}"

        # Email to client
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

        server = smtplib.SMTP("smtp.sendgrid.net", 587)
        server.starttls()
        server.login("apikey", API_KEY)
        server.sendmail(sender, recipient, message.as_string())
        print("✅ Booking request email sent to client.")

        # Email to provider
        if booking.safari.provider and booking.safari.provider.email:
            provider_email = booking.safari.provider.email
            total_provider_price = booking.safari.provider_price * booking.number_of_people

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
                <a href="{request_build_url('booking/confirm', booking.id)}">{request_build_url('booking/confirm', booking.id)}</a></p>
                <p>To <strong>CANCEL</strong> the booking, click here:<br>
                <a href="{request_build_url('booking/cancel', booking.id)}">{request_build_url('booking/cancel', booking.id)}</a></p>
                <p>Best regards,<br>The TourSafariAfrica Team</p>
              </body>
            </html>
            """

            provider_message = MIMEText(provider_body, "html")
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

        # Email client
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

        server = smtplib.SMTP("smtp.sendgrid.net", 587)
        server.starttls()
        server.login("apikey", API_KEY)
        server.sendmail(sender, booking.client_email, message_client.as_string())

        print("✅ Confirmation email sent to client.")

        # Email provider
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

def request_build_url(path, booking_id):
    # Build full URL for email links; replace 'example.com' with your domain
    return f"https://example.com/{path}/{booking_id}"
