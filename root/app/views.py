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

    error_message = None  # To display errors in the template

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

            # Validate min/max participants
            if safari.min_people and number_of_people < safari.min_people:
                error_message = f"Minimum number of people is {safari.min_people}."
            elif safari.max_people and number_of_people > safari.max_people:
                error_message = f"Maximum number of people is {safari.max_people}."

            if error_message:
                return render(request, 'app/safari_detail.html', {
                    'safari': safari,
                    'highlight_lines': highlight_lines,
                    'error_message': error_message,
                    'price_per_person': safari.client_price,
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

            # Send email to the client
            try:
                --
                sender = "pedro.tenza@outlook.com"
                recipient = email

                client_body = f"""
Dear {name},

Thank you for your booking request for the safari: {safari.name}
Selected date: {date}

Price per person: ${safari.client_price}
Number of Participants: {number_of_people}
Total price: ${safari.client_price * number_of_people}

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

                # Email to provider in English
                if provider_email:
                    total_provider_price = safari.provider_price * number_of_people
                    provider_body = f"""
Hello {safari.provider.name},

A new booking request has been made for the safari: {safari.name}  
Selected date: {date}  

Price per person: $        {safari.provider_price}  
Number of participants:    {number_of_people}  
Amount to be paid to you: ${total_provider_price}  

Client's name: {name}   
Client's age:  {age}  
Nationality:   {nationality} 

To CONFIRM the booking, please click the following link:  
{confirm_url}  

To CANCEL the booking, please click the following link:  
{cancel_url}  

Regards,  
The TOURSAFRICASAFARI Team
"""
                    provider_message = MIMEText(provider_body)
                    provider_message["Subject"] = "New Safari Booking Request"
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
        'safari': safari,
        'highlight_lines': highlight_lines,
        'error_message': error_message,
        'price_per_person': safari.client_price,
    })


def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.confirmed_by_provider = True
    booking.save()
    return HttpResponse("✅ Booking confirmed successfully.")


def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return HttpResponse("❌ Booking canceled successfully.")
