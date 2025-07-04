from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_invoice_pdf(booking, for_provider=False):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "TourSafariAfrica Invoice")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 90, f"Activity: {booking.safari.name}")
    c.drawString(50, height - 110, f"Date: {booking.date.strftime('%d-%m-%Y')}")
    c.drawString(50, height - 130, f"Participants: {booking.number_of_people}")

    if for_provider:
        price = booking.safari.provider_price * booking.number_of_people
        c.drawString(50, height - 150, f"Amount to Receive: ${price:.2f}")
    else:
        price = booking.safari.client_price * booking.number_of_people
        c.drawString(50, height - 150, f"Total Price: ${price:.2f}")

    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
