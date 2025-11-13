"""
Servicio para enviar correos electrónicos
"""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

async def enviar_email(to_email: str, subject: str, body: str) -> None:
    """
    Envía un correo electrónico.
    
    Args:
        to_email: Correo del destinatario
        subject: Asunto del correo
        body: Cuerpo del correo
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        
        logger.info(f"[EMAIL] Correo enviado a {to_email}")
    except Exception as e:
        logger.error(f"[EMAIL] Error enviando correo a {to_email}: {str(e)}")
        raise Exception(f"Error enviando correo: {str(e)}")