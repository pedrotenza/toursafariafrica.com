from datetime import datetime
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from app.models import Booking, Participant
from .email_service import (
    send_booking_request_email,
    send_booking_confirmation_emails,
    send_booking_cancellation_emails
)


def create_booking(post_data, safari, request):
    """
    Crea una reserva y sus participantes.
    Devuelve (booking, None) si todo va bien, o (None, mensaje_error) si hay un fallo.
    """
    try:
        print("📩 post_data recibido:", post_data)

        # Campos obligatorios
        name = post_data.get('name')
        email = post_data.get('email')
        date_str = post_data.get('date')
        number_of_people_str = post_data.get('number_of_people', '1')

        if not name:
            return None, "El campo 'name' es obligatorio."
        if not email:
            return None, "El campo 'email' es obligatorio."
        if not date_str:
            return None, "El campo 'date' es obligatorio."

        # Número de personas
        try:
            number_of_people = int(number_of_people_str)
            if number_of_people <= 0:
                return None, "El número de personas debe ser mayor a 0."
        except ValueError:
            return None, "Número de personas inválido."

        # Validar límites del safari
        if safari.min_people and number_of_people < safari.min_people:
            return None, f"El mínimo de personas para este safari es {safari.min_people}."
        if safari.max_people and number_of_people > safari.max_people:
            return None, f"El máximo de personas para este safari es {safari.max_people}."

        # Fecha
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None, "Formato de fecha inválido. Use YYYY-MM-DD."


        # Teléfono (opcional)
        country_code = post_data.get('client_phone_prefix', '').strip() or None
        phone = post_data.get('client_phone_number', '').strip() or None

        
        # Remove leading 0 if exists
        if phone and phone.startswith('0'):
            phone = phone[1:]



        # Crear booking
        booking = Booking.objects.create(
            safari=safari,
            client_name=name,
            client_email=email,
            client_phone_prefix=country_code,
            client_phone_number=phone,
            date=date,
            number_of_people=number_of_people,
            payment_status='pending',
            confirmed_by_provider=False
        )

        # Capturar participantes
        participants = []
        for i in range(1, number_of_people + 1):
            nationality_key = f'participant_nationality_{i}'
            age_key = f'participant_age_{i}'
            nationality = post_data.get(nationality_key)
            age_str = post_data.get(age_key)

            if nationality and age_str:
                try:
                    age = int(age_str)
                    if age > 0:
                        participants.append(Participant(
                            booking=booking,
                            nationality=nationality,
                            age=age
                        ))
                    else:
                        print(f"⚠️ Edad inválida para participante {i}: {age}")
                except ValueError:
                    print(f"⚠️ Edad no es un número para participante {i}: {age_str}")
            else:
                print(f"⚠️ Datos incompletos para participante {i}: nacionalidad={nationality}, edad={age_str}")

        if not participants:
            booking.delete()  # Eliminar booking vacío
            return None, "Los datos de los participantes están incompletos o inválidos."

        Participant.objects.bulk_create(participants)
        print(f"✅ Booking creado correctamente: {booking.id} con {len(participants)} participantes.")

        # Enviar email
        send_booking_request_email(booking, request)
        print("📧 Email de solicitud enviado.")

        return booking, None

    except Exception as e:
        import traceback
        print("❌ Error en create_booking:")
        traceback.print_exc()
        return None, f"Error procesando los datos de la reserva: {e}"


def confirm_booking_service(booking_id, request):
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        booking.confirmed_by_provider = True
        booking.payment_status = 'paid'
        booking.payment_date = now()
        booking.provider_response_date = now()
        booking.save()

        send_booking_confirmation_emails(booking, request)

        return """
        <h1>✅ Booking confirmed successfully</h1>
        <p>The payment has been processed (simulated).</p>
        <p>Confirmation emails with invoices have been sent to both client and provider.</p>
        <p><a href="/">Return to home</a></p>
        """
    except Exception as e:
        import traceback
        print("❌ Error confirming booking:")
        traceback.print_exc()
        return """
        <h1>❌ Error confirming booking</h1>
        <p>Something went wrong.</p>
        <p><a href="/">Return to home</a></p>
        """


def cancel_booking_service(booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id)

        if booking.payment_status == 'paid':
            print(f"🔄 Simulating refund for booking {booking_id}")

        booking.provider_response_date = now()
        booking.payment_status = 'canceled'
        booking.save()

        send_booking_cancellation_emails(booking)

        return """
        <h1>❌ Booking canceled successfully</h1>
        <p>The booking has been marked as canceled and notifications were sent.</p>
        <p><a href="/">Return to home</a></p>
        """
    except Exception as e:
        import traceback
        print("❌ Error canceling booking:")
        traceback.print_exc()
        return """
        <h1>❌ Error canceling booking</h1>
        <p>Something went wrong.</p>
        <p><a href="/">Return to home</a></p>
        """
