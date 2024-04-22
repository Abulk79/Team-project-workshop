from email.message import EmailMessage
import ssl
import smtplib
from .. import secret

def sendmail(to, body):
    fromMail = 'teamprojectworkshop@mail.ru'
    port = 465
    password = secret.PASSWORD_EMAIL

    message = EmailMessage()
    message['From'] = fromMail
    message['To'] = to
    message['Subject'] = 'Подтверждение аккаунта'
    message.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.mail.ru', port, context=context) as server:
        server.login(fromMail, password)
        server.send_message(message)