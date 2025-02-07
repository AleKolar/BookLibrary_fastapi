import os
import smtplib
from email.mime.text import MIMEText
from celery import shared_task
from dotenv import load_dotenv
import logging


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

@shared_task
def send_email(to_email: str, subject: str, body: str):
    """Отправляет электронное письмо с использованием SMTP."""

    # Создание MIMEText объекта
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = to_email

    try:
        logger.info(f"Connecting to {EMAIL_HOST}:{EMAIL_PORT} as {EMAIL_HOST_USER}")
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            logger.info("Logging in...")
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, to_email, msg.as_string())
            logger.info(f"Email sent to {to_email}")
    except smtplib.SMTPAuthenticationError:
        logger.error("Authentication failed, please check your email credentials.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")


# if __name__ == "__main__":
#     send_email('alek.kolark@gmail.com','Test Subject', 'This is a test email from Python!')
