import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import config_project


def send_email(email_to, token):
    smtp_server = 'smtp.gmail.com'
    port = 587

    sender_email = config_project.email_sender
    password = config_project.email_password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email_to
    message['Subject'] = "Подтверждение почты - Sensus Weather"

    body = token
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, email_to, text)
        print('Письмо успешно отправлено!')
    except Exception as e:
        print(f'Ошибка: {e}')
    finally:
        server.quit()  # Завершение сессии SMTP
