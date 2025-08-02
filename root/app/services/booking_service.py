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
    error_message = None
    try:
        name = post_data['name']
        email = post_data['email']
        country_code = post_data.get('country_code', '')  # Obtener prefijo
        phone = post_data.get('phone', '')
        full_phone = f"{country_code}{phone}".strip()  # Combinar prefijo + teléfono
        
        date_str = post_data['date']
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        number_of_people = int(post_data.get('number_of_people', 1))

        if safari.min_people and number_of_people < safari.min_people:
            return None, f"Minimum number of people is {safari.min_people}."
        if safari.max_people and number_of_people > safari.max_people:
            return None, f"Maximum number of people is {safari.max_people}."

        # Crear la reserva con el teléfono completo
        booking = Booking.objects.create(
            safari=safari,
            client_name=name,
            client_email=email,
            client_phone=full_phone,
            date=date,
            number_of_people=number_of_people,
            payment_status='pending',
            confirmed_by_provider=False
        )

        # Capturar los participantes dinámicos
        participants = []
        for i in range(1, number_of_people + 1):
            nationality_key = f'participant_nationality_{i}'
            age_key = f'participant_age_{i}'

            nationality = post_data.get(nationality_key)
            age = post_data.get(age_key)

            if nationality and age:
                try:
                    age = int(age)
                    if age > 0:
                        participants.append(Participant(
                            booking=booking,
                            nationality=nationality,
                            age=age
                        ))
                except ValueError:
                    continue  # Ignora edades inválidas

        if not participants:
            return None, "Participant data is incomplete or invalid."

        Participant.objects.bulk_create(participants)

        # Enviar notificaciones
        send_booking_request_email(booking, request)
        return booking, None

    except Exception as e:
        print(f"❌ Error in create_booking: {e}")
        return None, "Error processing booking data."


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
        print(f"❌ Error confirming booking: {e}")
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
        print(f"❌ Error canceling booking: {e}")
        return """
        <h1>❌ Error canceling booking</h1>
        <p>Something went wrong.</p>
        <p><a href="/">Return to home</a></p>
        """
