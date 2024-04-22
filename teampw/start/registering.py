from django.shortcuts import render, redirect
from . import models
from django.http import HttpResponse
import re
from .emailteampw import sendmail
import random
import hashlib
from django.contrib.auth import login, logout

def home(req):
    context = {}
    if req.user.is_authenticated:
        user = models.User.objects.get(name=req.user.name)
        team = models.TeamMembership.objects.filter(user=req.user).first()

        context['team'] = team
        context['user'] = user

    return render(req, 'home.html', context)

def registeraccount(req):
    return render(req,'registeraccount.html', {})

def loginaccount(req):
    return render(req, 'login.html', {})

def registerteam(req):
    return render(req,'registerteam.html', {})

def login_api(req):
    name = req.POST['name']
    password = hashlib.md5(req.POST['password'].encode()).hexdigest()

    user = models.User.objects.filter(name=name, password=password).first()
    if user:
        login(req, user)
        return redirect('/users/' + name + '/')
    else:
        return HttpResponse('Неверное имя или пароль')

def verifyemail_api(req):
    name = req.POST['name']
    email = req.POST['email']
    password = hashlib.md5(req.POST['password'].encode()).hexdigest()

    if len(name) < 3:
        return HttpResponse('Имя должно быть не менее 3 символов')
    if models.User.objects.filter(name=name).exists():
        return HttpResponse('Аккаунт с таким именем уже существует')
    if not re.fullmatch(r'^[a-zA-Z0-9_-]*', name):
        return HttpResponse('Имя должно содержать только латинские буквы, цифры и знаки "-", "_"')

    code = hex(random.getrandbits(128))

    unverUser = models.UnverifiedUser.objects.filter(name=name).first()
    if unverUser:
        unverUser.delete()

    models.UnverifiedUser.objects.create(name=name, email=email, password=password, code=code)

    reference = """
    Пройдите по ссылке для подтверждения аккаунта:
    http://localhost:8000/api/registeraccount?name={name}&code={code}
    """.format(name=name, code=code)

    sendmail(email, reference)

    return HttpResponse('Письмо отправлено на почту для подтверждения аккаунта')

def registeraccount_api(req):
    name = req.GET['name']
    code = req.GET['code']

    unverUser = models.UnverifiedUser.objects.get(name=name, code=code)
    user = models.User.objects.create_user(name=unverUser.name, email=unverUser.email, password=unverUser.password)
    unverUser.delete()
    login(req, user)

    return redirect('/users/' + user.name + '/')

def registerteam_api(req):
    if not req.user.is_authenticated:
        return HttpResponse('Вы не авторизованы')

    name = req.POST['name']
    info = req.POST['info']

    user = req.user

    if len(name) < 3:
        return HttpResponse('Название команды должно состоять не менее из 3 символов')
    if not re.fullmatch(r'^[a-zA-Z0-9_-]*', name):
        return HttpResponse('Название команды должно состоять только из латинских букв, цифр и знаков "-", "_"')
    if models.Team.objects.filter(name=name).exists():
        return HttpResponse('Команда с таким именем уже существует')
    if models.TeamMembership.objects.filter(user=user).exists():
        return HttpResponse('Вы уже состоите в команде')
    
    userad = models.UserAd.objects.filter(user=user).first()
    if userad:
        userad.delete()

    models.Invite.objects.filter(receiver=user).delete()
    models.Request.objects.filter(sender=user).delete()

    team = models.Team.objects.create(name=name, info=info, owner=user)
    models.TeamMembership.objects.create(user=user, team=team)

    return redirect('/teams/' + name + '/')

def logout_api(req):
    logout(req)
    return redirect('/')