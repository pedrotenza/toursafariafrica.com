import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from .invoice_service import generate_invoice_pdf
import os
from dotenv import load_dotenv
from django.urls import reverse
from ..models import Participant  # Importación relativa corregida

load_dotenv()

SMTP_USER = os.getenv('BREVO_SMTP_USER')
SMTP_PASSWORD = os.getenv('BREVO_SMTP_PASSWORD')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')


def request_build_url(request, path_name, booking_id):
    relative_url = reverse(path_name, args=[booking_id])
    return request.build_absolute_uri(relative_url)


def send_booking_request_email(booking, request, participants_data=None):
    try:
        sender = SENDER_EMAIL
        recipient = booking.client_email
        subject = f"{booking.safari.name} – Booking Request – {booking.date.strftime('%d.%m.%Y')}"

        # Procesar información de participantes
        participants_info = []
        participants_list = []
        if participants_data:
            for idx, participant in enumerate(participants_data, 1):
                participants_info.append(
                    f"• Participant {idx}: Age {participant.get('age', 'N/A')} | Nationality: {participant.get('nationality', 'N/A')}"
                )
            participants_list = participants_data
        else:
            try:
                participants = Participant.objects.filter(booking=booking).order_by('id')
                participants_list = participants
                for idx, participant in enumerate(participants, 1):
                    participants_info.append(
                        f"• Participant {idx}: Age {participant.age} | Nationality: {participant.nationality}"
                    )
            except Exception as e:
                print(f"Error getting participants: {str(e)}")

        participants_text = "\n".join(participants_info) if participants_info else "No participant details provided"

        # Email para el cliente (HTML)
        client_body = f"""
        <html>
          <body>
            <p>Dear {booking.client_name},</p>
            <p>Thank you for your booking request:</p>
            <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
            <pre>
Date:          {booking.date.strftime("%d-%m-%Y")}
Participants:  {booking.number_of_people}
Total Price:   {booking.safari.client_price * booking.number_of_people:.2f}
            </pre>
            <p>Participants Details:</p>
            <pre>{participants_text}</pre>
            <p>We will contact you soon with the confirmation.</p>
            <p>Best regards,<br>TourSafariAfrica Team</p>
          </body>
        </html>
        """

        message = MIMEText(client_body, "html")
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = recipient

        with smtplib.SMTP("smtp-relay.brevo.com", 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(sender, recipient, message.as_string())
            print(f"Booking request email sent to client")

            if booking.safari.provider and hasattr(booking.safari.provider, 'email'):
                confirm_url = request_build_url(request, 'confirm_booking', booking.id)
                cancel_url = request_build_url(request, 'cancel_booking', booking.id)

                # Para el proveedor, formato HTML con links clicables
                provider_body = f"""
                <html>
                  <body>
                    <p>Hello {booking.safari.provider.name if hasattr(booking.safari.provider, 'name') else 'Simon'},</p>
                    <p>A new booking request has been made for the safari:</p>
                    <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
                    <pre>
Selected Date:             {booking.date.strftime("%d-%m-%Y")}
Price per Person:          {booking.safari.provider_price:.2f}
Number of Participants:    {booking.number_of_people}
---------------------------------------------
Amount to Be Paid to You:  {booking.safari.provider_price * booking.number_of_people:.2f}
                    </pre>
                    <p>Client Details:</p>
                    <pre>
Name:        {booking.client_name}
Age:         {participants_list[0].age if participants_list else 'N/A'}
Nationality: {participants_list[0].nationality if participants_list else 'N/A'}
                    </pre>
                    <p>To <b>CONFIRM</b> the booking, click here:<br>
                       <a href="{confirm_url}">{confirm_url}</a></p>
                    <p>To <b>CANCEL</b> the booking, click here:<br>
                       <a href="{cancel_url}">{cancel_url}</a></p>
                    <p>Best regards,<br>
                    The TourSafariAfrica Team</p>
                  </body>
                </html>
                """

                provider_message = MIMEMultipart()
                provider_message['Subject'] = subject
                provider_message['From'] = sender
                provider_message['To'] = booking.safari.provider.email
                provider_message.attach(MIMEText(provider_body, "html"))

                server.sendmail(sender, booking.safari.provider.email, provider_message.as_string())
                print(f"Booking request sent to provider")

    except Exception as e:
        print(f"Error sending emails: {str(e)}")


def send_booking_confirmation_emails(booking, request):
    try:
        sender = SENDER_EMAIL
        subject = f"{booking.safari.name} – Booking Confirmed – {booking.date.strftime('%d.%m.%Y')}"

        # Obtener detalles de participantes
        participants_info = []
        try:
            participants = Participant.objects.filter(booking=booking).order_by('id')
            for idx, participant in enumerate(participants, 1):
                participants_info.append(
                    f"• Participant {idx}: Age {participant.age} | Nationality: {participant.nationality}"
                )
        except Exception as e:
            print(f"Error getting participants: {str(e)}")

        participants_text = "\n".join(participants_info) if participants_info else "No participant details"

        client_body = f"""
        <html>
          <body>
            <p>Dear {booking.client_name},</p>
            <p>Your booking has been confirmed:</p>
            <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
            <pre>
Date:          {booking.date.strftime("%d-%m-%Y")}
Participants:  {booking.number_of_people}
Total Price:   {booking.safari.client_price * booking.number_of_people:.2f}
            </pre>
            <p>Participants Details:</p>
            <pre>{participants_text}</pre>
            <p>Your invoice is attached.</p>
            <p>Best regards,<br>TourSafariAfrica Team</p>
          </body>
        </html>
        """

        with smtplib.SMTP("smtp-relay.brevo.com", 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)

            # Email para cliente
            message_client = MIMEMultipart()
            message_client["Subject"] = subject
            message_client["From"] = sender
            message_client["To"] = booking.client_email
            message_client.attach(MIMEText(client_body, "html"))

            invoice_client = generate_invoice_pdf(booking, for_provider=False)
            part_client = MIMEApplication(invoice_client, Name="Invoice.pdf")
            part_client['Content-Disposition'] = 'attachment; filename="Invoice.pdf"'
            message_client.attach(part_client)

            server.sendmail(sender, booking.client_email, message_client.as_string())
            print("Confirmation email sent to client")

            # Email para proveedor
            if booking.safari.provider and hasattr(booking.safari.provider, 'email'):
                provider_body = f"""
                <html>
                  <body>
                    <p>Booking confirmed:</p>
                    <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
                    <pre>
Date:          {booking.date.strftime("%d-%m-%Y")}
Participants:  {booking.number_of_people}
Amount:        {booking.safari.provider_price * booking.number_of_people:.2f}
                    </pre>
                    <p>Your invoice is attached.</p>
                  </body>
                </html>
                """

                provider_message = MIMEMultipart()
                provider_message["Subject"] = subject
                provider_message["From"] = sender
                provider_message["To"] = booking.safari.provider.email
                provider_message.attach(MIMEText(provider_body, "html"))

                invoice_provider = generate_invoice_pdf(booking, for_provider=True)
                part_provider = MIMEApplication(invoice_provider, Name="Provider_Invoice.pdf")
                part_provider['Content-Disposition'] = 'attachment; filename="Provider_Invoice.pdf"'
                provider_message.attach(part_provider)

                server.sendmail(sender, booking.safari.provider.email, provider_message.as_string())
                print("Confirmation email sent to provider")

    except Exception as e:
        print(f"Error sending confirmation emails: {str(e)}")


def send_booking_cancellation_emails(booking):
    try:
        sender = SENDER_EMAIL
        subject = f"{booking.safari.name} – Booking Canceled – {booking.date.strftime('%d.%m.%Y')}"

        with smtplib.SMTP("smtp-relay.brevo.com", 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)

            # Email para cliente
            client_body = f"""
            <html>
              <body>
                <p>Dear {booking.client_name},</p>
                <p>Your booking has been canceled:</p>
                <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
                <pre>
Date:          {booking.date.strftime("%d-%m-%Y")}
Participants:  {booking.number_of_people}
                </pre>
                <p>The cancellation receipt is attached.</p>
                <p>Best regards,<br>TourSafariAfrica Team</p>
              </body>
            </html>
            """

            msg_client = MIMEMultipart()
            msg_client["Subject"] = subject
            msg_client["From"] = sender
            msg_client["To"] = booking.client_email
            msg_client.attach(MIMEText(client_body, "html"))

            invoice_pdf = generate_invoice_pdf(booking, for_provider=False)
            part_cli = MIMEApplication(invoice_pdf, Name="Cancellation_Receipt.pdf")
            part_cli["Content-Disposition"] = 'attachment; filename="Cancellation_Receipt.pdf"'
            msg_client.attach(part_cli)

            server.sendmail(sender, booking.client_email, msg_client.as_string())
            print("Cancellation email sent to client")

            # Email para proveedor
            if booking.safari.provider and hasattr(booking.safari.provider, 'email'):
                provider_body = f"""
                <html>
                  <body>
                    <p>Booking canceled:</p>
                    <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
                    <pre>
Date:          {booking.date.strftime("%d-%m-%Y")}
Participants:  {booking.number_of_people}
                    </pre>
                    <p>The cancellation receipt is attached.</p>
                  </body>
                </html>
                """

                msg_prov = MIMEMultipart()
                msg_prov["Subject"] = subject
                msg_prov["From"] = sender
                msg_prov["To"] = booking.safari.provider.email
                msg_prov.attach(MIMEText(provider_body, "html"))

                invoice_pdf_prov = generate_invoice_pdf(booking, for_provider=True)
                part_prv = MIMEApplication(invoice_pdf_prov, Name="Provider_Cancellation_Receipt.pdf")
                part_prv["Content-Disposition"] = 'attachment; filename="Provider_Cancellation_Receipt.pdf"'
                msg_prov.attach(part_prv)

                server.sendmail(sender, booking.safari.provider.email, msg_prov.as_string())
                print("Cancellation email sent to provider")

    except Exception as e:
        print(f"Error sending cancellation emails: {str(e)}")
