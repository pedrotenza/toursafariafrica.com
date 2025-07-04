from datetime import datetime
from django.shortcuts import get_object_or_404
from app.models import Booking
from .email_service import send_booking_request_email, send_booking_confirmation_emails

def create_booking(post_data, safari, request): 

    error_message = None
    try:
        name = post_data['name']
        email = post_data['email']
        phone = post_data.get('phone', '')
        nationality = post_data.get('nationality', '')
        age = int(post_data.get('age', 0))
        date_str = post_data['date']
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        number_of_people = int(post_data.get('number_of_people', 1))

        if safari.min_people and number_of_people < safari.min_people:
            error_message = f"Minimum number of people is {safari.min_people}."
            return None, error_message
        if safari.max_people and number_of_people > safari.max_people:
            error_message = f"Maximum number of people is {safari.max_people}."
            return None, error_message

        booking = Booking.objects.create(
            safari=safari,
            client_name=name,
            client_email=email,
            client_phone=phone,
            client_nationality=nationality,
            client_age=age,
            date=date,
            number_of_people=number_of_people,
            payment_status='pending',
            confirmed_by_provider=False
        )

        send_booking_request_email(booking, request)
        return booking, None
    except Exception as e:
        error_message = "Error processing booking data."
        print(f"❌ Error in create_booking: {e}")
        return None, error_message


def confirm_booking_service(booking_id, request):
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        # Simulate payment processing
        booking.confirmed_by_provider = True
        booking.payment_status = 'paid'
        booking.payment_date = datetime.now()
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
            # Simulate refund
            print(f"🔄 Simulating refund for booking {booking_id}")
        booking.delete()
        return """
        <h1>❌ Booking canceled successfully</h1>
        <p>Any simulated payments have been refunded.</p>
        <p><a href="/">Return to home</a></p>
        """
    except Exception as e:
        print(f"❌ Error canceling booking: {e}")
        return """
        <h1>❌ Error canceling booking</h1>
        <p>Something went wrong.</p>
        <p><a href="/">Return to home</a></p>
        """
