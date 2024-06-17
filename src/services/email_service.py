import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import config_project




def send_email(email_to, token):
    smtp_server = 'smtp.yandex.ru'
    port = 587

    sender_email = config_project.email_sender
    password = config_project.email_password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email_to
    message['Subject'] = "Подтверждение почты - Sensus Weather"

    body = generate_email_confirmation_html(token)
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


def generate_email_confirmation_html(confirmation_link):
    email_confirmation_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Email подтверждения почты</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #000;
          color: #fff;
          padding: 20px;
        }}
        .container {{
          max-width: 600px;
          margin: 0 auto;
          text-align: center;
        }}
        .header {{
          background-color: #000;
          padding: 20px;
        }}
        .header h1 {{
          color: #00f;
        }}
        .content {{
          padding: 20px;
        }}
        .button {{
          display: inline-block;
          padding: 10px 20px;
          background-color: #00f;
          color: #fff;
          text-decoration: none;
          border-radius: 5px;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>Подтверждение адреса электронной почты</h1>
        </div>
        <div class="content">
          <p>Здравствуйте!</p>
          <p>Спасибо, что зарегистрировались в сервисе погоды "Sensus". Чтобы завершить процесс регистрации, пожалуйста, подтвердите свой адрес электронной почты, кликнув на кнопку ниже:</p>
          <a href="{confirmation_link}" class="button">Подтвердить почту</a>
          <p>Если у вас возникли проблемы с подтверждением, пожалуйста, свяжитесь с нами по адресу support@sensus.com</p>
        </div>
      </div>
    </body>
    </html>
    """
    return email_confirmation_html