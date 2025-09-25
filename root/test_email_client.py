import smtplib
from email.mime.text import MIMEText
import os
from pathlib import Path
from dotenv import load_dotenv

# --- Cargar .env desde la raíz del proyecto ---
env_path = Path(__file__).resolve().parent / '.env'  # Ajusta si tu .env está un nivel arriba
load_dotenv(dotenv_path=env_path)

# --- Variables de entorno ---
SMTP_SERVER = os.getenv('BREVO_SMTP_SERVER')
SMTP_PORT = int(os.getenv('BREVO_SMTP_PORT'))  # ahora debería ser 587
SMTP_USER = os.getenv('BREVO_SMTP_USER')
SMTP_PASSWORD = os.getenv('BREVO_SMTP_PASSWORD')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')

recipient = 'pedro.tenza@hotmail.com'

msg = MIMEText("Este es un correo de prueba enviado desde Django usando Brevo SMTP.")
msg['Subject'] = "Test Brevo – Client Email"
msg['From'] = SENDER_EMAIL
msg['To'] = recipient

with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    server.set_debuglevel(1)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(SENDER_EMAIL, recipient, msg.as_string())

print(f"Correo enviado a {recipient}")
