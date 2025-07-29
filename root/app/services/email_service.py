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
            participants_list = participants_data
            for idx, participant in enumerate(participants_data, 1):
                participants_info.append(
                    f"• Participant {idx}: Age {participant.get('age', 'N/A')} | Nationality: {participant.get('nationality', 'N/A')}"
                )
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

        # Construir tabla HTML para detalles de participantes (cliente)
        if participants_list:
            participants_table = """
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 600px;">
              <thead style="background-color: #f2f2f2;">
                <tr>
                  <th>Participant</th>
                  <th>Age</th>
                  <th>Nationality</th>
                </tr>
              </thead>
              <tbody>
            """
            for i, p in enumerate(participants_list, 1):
                if isinstance(p, dict):
                    age = p.get('age', 'N/A')
                    nationality = p.get('nationality', 'N/A')
                else:
                    age = getattr(p, 'age', 'N/A')
                    nationality = getattr(p, 'nationality', 'N/A')
                participants_table += f"""
                <tr>
                  <td style="text-align: center;">{i}</td>
                  <td style="text-align: center;">{age}</td>
                  <td style="text-align: center;">{nationality}</td>
                </tr>
                """
            participants_table += """
              </tbody>
            </table>
            """
        else:
            participants_table = "<p>No participant details provided.</p>"

        # Email para el cliente (HTML) con tabla en lugar de <pre>
        client_body = f"""
        <html>
          <body>
            <p>Dear {booking.client_name},</p>
            <p>Thank you for your booking request:</p>
            <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
            <pre style="font-family: monospace; font-size: 14px;">
        Selected Date:           {booking.date.strftime("%d-%m-%Y")}
        Price per Person:        {booking.safari.client_price:.2f}
        Number of Participants:  {booking.number_of_people}
        _________________________________________
        Amount to Be Paid:       {(booking.safari.client_price * booking.number_of_people):.2f}
            </pre>
            <p>Participants Details:</p>
            {participants_table}
            <p>Your booking awaits operator confirmation. We'll contact you once confirmed — no payment will be processed until then.</p>
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

                # Construir tabla HTML para detalles de participantes para el provider (igual que para el cliente)
                if participants_list:
                    participants_table_provider = """
                    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 600px;">
                      <thead style="background-color: #f2f2f2;">
                        <tr>
                          <th>Participant</th>
                          <th>Age</th>
                          <th>Nationality</th>
                        </tr>
                      </thead>
                      <tbody>
                    """
                    for i, p in enumerate(participants_list, 1):
                        if isinstance(p, dict):
                            age = p.get('age', 'N/A')
                            nationality = p.get('nationality', 'N/A')
                        else:
                            age = getattr(p, 'age', 'N/A')
                            nationality = getattr(p, 'nationality', 'N/A')
                        participants_table_provider += f"""
                        <tr>
                          <td style="text-align: center;">{i}</td>
                          <td style="text-align: center;">{age}</td>
                          <td style="text-align: center;">{nationality}</td>
                        </tr>
                        """
                    participants_table_provider += """
                      </tbody>
                    </table>
                    """
                else:
                    participants_table_provider = "<p>No participant details provided.</p>"

                provider_body = f"""
                <html>
                  <body>
                    <p>Hello {booking.safari.provider.name if hasattr(booking.safari.provider, 'name') else 'Simon'},</p>
                    <p>A new booking request has been made for the Activity:</p>
                    <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
                    <pre>
Selected Date:             {booking.date.strftime("%d-%m-%Y")}
Price per Person:          {booking.safari.provider_price:.2f}
Number of Participants:    {booking.number_of_people}
_________________________________________
Amount to Be Paid to You:  {booking.safari.provider_price * booking.number_of_people:.2f}
                    </pre>
                    <p>Client Details:</p>
                    <p><b>Name:</b> {booking.client_name}</p>
                    <p><b>Participants Details:</b></p>
                    {participants_table_provider}
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

        # Obtener participantes
        participants = Participant.objects.filter(booking=booking).order_by('id')
        participants_list = list(participants)  # Convertir a lista para reutilizar lógica

        # Construir tabla HTML para detalles de participantes (cliente)
        if participants_list:
            participants_table = """
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 600px;">
              <thead style="background-color: #f2f2f2;">
                <tr>
                  <th>Participant</th>
                  <th>Age</th>
                  <th>Nationality</th>
                </tr>
              </thead>
              <tbody>
            """
            for i, p in enumerate(participants_list, 1):
                age = getattr(p, 'age', 'N/A')
                nationality = getattr(p, 'nationality', 'N/A')
                participants_table += f"""
                <tr>
                  <td style="text-align: center;">{i}</td>
                  <td style="text-align: center;">{age}</td>
                  <td style="text-align: center;">{nationality}</td>
                </tr>
                """
            participants_table += """
              </tbody>
            </table>
            """
        else:
            participants_table = "<p>No participant details provided.</p>"

        # Get provider contact details if available
        provider_contact = ""
        if booking.safari.provider and hasattr(booking.safari.provider, 'email'):
            provider_contact = f"""
            <p><strong>Provider Contact Details:</strong></p>
            <p>Name: {getattr(booking.safari.provider, 'name', 'N/A')}<br>
               Email: {booking.safari.provider.email}<br>
               Phone: {getattr(booking.safari.provider, 'phone', 'N/A')}</p>
            """

        # Email para el cliente (HTML) con toda la información
        client_body = f"""
        <html>
          <body>
            <p>Dear {booking.client_name},</p>
            <p>Your booking has been confirmed:</p>
            <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
            <pre style="font-family: monospace; font-size: 14px;">
Selected Date:           {booking.date.strftime("%d-%m-%Y")}
Price per Person:        {booking.safari.client_price:.2f}
Number of Participants:  {booking.number_of_people}
_________________________________________
Amount to Be Paid:       {(booking.safari.client_price * booking.number_of_people):.2f}
            </pre>
            <p><strong>Participants Details:</strong></p>
            {participants_table}
            {provider_contact}
            <p>Your invoice is attached to this email.</p>
            <p>If you have any questions, please don't hesitate to contact the provider directly or reply to this email.</p>
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
                participants_table_provider = """
                <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 600px;">
                  <thead style="background-color: #f2f2f2;">
                    <tr>
                      <th>Participant</th>
                      <th>Age</th>
                      <th>Nationality</th>
                    </tr>
                  </thead>
                  <tbody>
                """
                for i, p in enumerate(participants_list, 1):
                    age = getattr(p, 'age', 'N/A')
                    nationality = getattr(p, 'nationality', 'N/A')
                    participants_table_provider += f"""
                    <tr>
                      <td style="text-align: center;">{i}</td>
                      <td style="text-align: center;">{age}</td>
                      <td style="text-align: center;">{nationality}</td>
                    </tr>
                    """
                participants_table_provider += """
                  </tbody>
                </table>
                """

                provider_body = f"""
                <html>
                  <body>
                    <p>Hello {booking.safari.provider.name if hasattr(booking.safari.provider, 'name') else 'Provider'},</p>
                    <p>The following booking has been <strong>confirmed</strong>:</p>
                    <p style="font-size: 20px; font-weight: bold;">{booking.safari.name}</p>
                    <pre style="font-family: monospace;">
Date:                        {booking.date.strftime("%d-%m-%Y")}
Price per Person:            {booking.safari.provider_price:.2f}
Number of Participants:      {booking.number_of_people}
_________________________________________
Amount to Be Paid to You:    {(booking.safari.provider_price * booking.number_of_people):.2f}
                    </pre>
                    <p><b>Client Details:</b></p>
                    <p>Name: {booking.client_name}<br>
                       Email: {booking.client_email}<br>
                       Phone: {booking.client_phone}</p>
                    <p><b>Participants Details:</b></p>
                    {participants_table_provider}
                    <p>Your invoice is attached.</p>
                    <p>Best regards,<br>
                    The TourSafariAfrica Team</p>
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