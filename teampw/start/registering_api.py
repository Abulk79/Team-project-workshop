from django.shortcuts import redirect
from .models import *
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseForbidden
import re
from .auxiliary import *
import random
import hashlib
from django.contrib.auth import login, logout

def login_api(req):
    if req.method != 'POST':
        return HttpResponseNotFound('Неверный метод запроса')

    name = req.POST['name']
    password = hashlib.md5(req.POST['password'].encode()).hexdigest()

    user = User.objects.filter(name=name, password=password).first()
    if user:
        login(req, user)
        return redirect('/users/' + name + '/')
    
    else:
        return HttpResponseForbidden('Неверное имя или пароль')

def verify_email_api(req):
    if req.method != 'POST':
        return HttpResponseNotFound('Неверный метод запроса')

    name = req.POST['name']
    email = req.POST['email']
    password = hashlib.md5(req.POST['password'].encode()).hexdigest()

    if len(name) < 3:
        return HttpResponseBadRequest('Имя должно быть не менее 3 символов')
    
    if not re.fullmatch(r'^[a-zA-Z0-9_-]*', name):
        return HttpResponseBadRequest('Имя должно содержать только латинские буквы, цифры и знаки "-", "_"')
    
    if User.objects.filter(name=name).exists():
        return HttpResponseBadRequest('Аккаунт с таким именем уже существует')

    code = hex(random.getrandbits(128))

    unverUser = UnverifiedUser.objects.filter(name=name).first()
    if unverUser:
        unverUser.delete()

    UnverifiedUser.objects.create(
        name=name, 
        email=email, 
        password=password, 
        code=code
    )

    reference = """
    Пройдите по ссылке для подтверждения аккаунта:
    http://localhost:8000/api/registeraccount?name={name}&code={code}
    """.format(name=name, code=code)

    sendmail(email, reference)

    return HttpResponse('Письмо отправлено на почту для подтверждения аккаунта')

def register_account_api(req):
    name = req.GET['name']
    code = req.GET['code']

    unverUser = UnverifiedUser.objects.filter(name=name, code=code).first()
    if not unverUser:
        return HttpResponseNotFound('Пользователь не найден')
    
    user = User.objects.create_user(
        name=unverUser.name, 
        email=unverUser.email, 
        password=unverUser.password
    )
    
    unverUser.delete()
    login(req, user)

    return redirect('/users/' + user.name + '/')

@login_needed_and_post_method
def register_team_api(req):
    name = req.POST['name']
    info = req.POST['info']

    user = req.user

    if len(name) < 3:
        return HttpResponseBadRequest('Название команды должно состоять не менее из 3 символов')
    
    if not re.fullmatch(r'^[a-zA-Z0-9_-]*', name):
        return HttpResponseBadRequest('Название команды должно состоять только из латинских букв, цифр и знаков "-", "_"')
    
    if Team.objects.filter(name=name).exists():
        return HttpResponseBadRequest('Команда с таким именем уже существует')
    
    if TeamMembership.objects.filter(user=user).exists():
        return HttpResponseBadRequest('Вы уже состоите в команде')
    
    UserAd.objects.filter(user=user).delete()
    Invite.objects.filter(receiver=user).delete()
    Request.objects.filter(sender=user).delete()

    team = Team.objects.create(name=name, info=info, owner=user)
    TeamMembership.objects.create(user=user, team=team)

    return redirect('/teams/' + name + '/')

def logout_api(req):
    logout(req)
    return redirect('/')
