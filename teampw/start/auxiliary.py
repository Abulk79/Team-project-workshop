from email.message import EmailMessage
import ssl
import smtplib
from .secret import PASSWORD_EMAIL
from functools import wraps
from django.http import HttpResponseForbidden, HttpResponseNotFound


def send_mail(to, body):
    fromMail = 'teamprojectworkshop@mail.ru'
    port = 465
    password = PASSWORD_EMAIL

    message = EmailMessage()
    message['From'] = fromMail
    message['To'] = to
    message['Subject'] = 'Подтверждение аккаунта'
    message.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.mail.ru', port, context=context) as server:
        server.login(fromMail, password)
        server.send_message(message)

def login_needed_and_post_method(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        req = args[0]
        
        if req.method != 'POST':
            return HttpResponseNotFound('Неверный метод запроса')
        
        if not req.user.is_authenticated:
            return HttpResponseForbidden('Вы не авторизованы')
        
        return f(*args, **kwargs)

    return wrapper

def change_Ad(ad, project, role, skills):
    ad.project = project
    ad.role = role
    ad.skills = skills
    ad.save()