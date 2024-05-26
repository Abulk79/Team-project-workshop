from django.shortcuts import redirect
from .models import *
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from .auxiliary import *

@login_needed_and_post_method
def change_user_info_api(req):
    info = req.POST['info']
    contacts = req.POST['contacts']

    user = req.user
    user.info = info
    user.contacts = contacts
    user.save()

    return redirect('/users/' + req.user.name + '/')

@login_needed_and_post_method
def change_team_info_api(req):
    team = Team.objects.filter(owner=req.user).first()
    if not team:
        return HttpResponseNotFound('Вы не являетесь владельцем команды')

    info = req.POST['info']

    team.info = info
    team.save()

    return redirect('/teams/' + team.name + '/')

@login_needed_and_post_method
def invite_api(req, name):
    team = Team.objects.filter(owner=req.user).first()
    if not team:
        return HttpResponseNotFound('Вы не являетесь владельцем команды')
    
    receiver = User.objects.filter(name=name).first()
    if not receiver:
        return HttpResponseNotFound('Пользователя не существует')
    
    sender = req.user

    if TeamMembership.objects.filter(user=receiver).exists():
        return HttpResponseBadRequest('Пользователь уже состоит в команде')

    if Invite.objects.filter(team=team, sender=sender, receiver=name).exists():
        return HttpResponseBadRequest('Вы уже отправили приглашение')

    # Если запрос есть, человек вступает в команду
    request = Request.objects.filter(team=team, sender=receiver, receiver=sender).first()
    if request:
        userad = UserAd.objects.filter(user=receiver).first()
        if userad:
            userad.delete()

        Invite.objects.filter(receiver=receiver).delete()
        Request.objects.filter(sender=receiver).delete()

        TeamMembership.objects.create(team=team, user=receiver)
        return redirect('/teams/' + team.name + '/')

    Invite.objects.create(team=team, sender=sender, receiver=receiver)
    return HttpResponse('Вы успешно отправили приглашение на вступление в команду')

@login_needed_and_post_method
def request_api(req, name):
    sender = req.user
    receiver = User.objects.filter(name=name).first()
    if not receiver:
        return HttpResponseNotFound('Пользователя не существует')

    team = Team.objects.filter(owner=receiver).first()
    if not team:
        return HttpResponseNotFound('Пользователь не является владельцем команды')

    if TeamMembership.objects.filter(user=sender).exists():
        return HttpResponseBadRequest('Вы и так состоите в команде')
    
    if Request.objects.filter(team=team, sender=sender, receiver=receiver).exists():
        return HttpResponseBadRequest('Вы уже отправили запрос')

    invite = Invite.objects.filter(team=team, sender=receiver, receiver=sender)

    # Если приглашение есть, то вступаем в команду
    if invite:
        userad = UserAd.objects.filter(user=sender).first()
        if userad:
            userad.delete()

        Invite.objects.filter(receiver=sender).delete()
        Request.objects.filter(sender=sender).delete()

        TeamMembership.objects.create(team=team, user=sender)
        return redirect('/teams/' + team.name + '/')

    Request.objects.create(team=team, sender=sender, receiver=receiver)
    return HttpResponse('Вы успешно отправили запрос на вступление в команду')

@login_needed_and_post_method
def leave_api(req):
    team = Team.objects.filter(owner=req.user).first()
    if team:
        team.delete()
        return redirect('/')

    membership = TeamMembership.objects.filter(user=req.user).first()
    if membership:
        membership.delete()
        return redirect('/')
    
    else:
        return HttpResponseNotFound('Вы не состоите в команде')

@login_needed_and_post_method
def kick_api(req, name):
    if req.user.name == name:
        return HttpResponseBadRequest('Вы не можете выгнать самого себя')

    team = Team.objects.filter(owner=req.user).first()
    if not team:
        return HttpResponseNotFound('Вы не являетесь владельцем команды')
    
    membership = TeamMembership.objects.filter(team=team, user=name).first()
    if not membership:
        return HttpResponseNotFound('Пользователь не найден')
    
    membership.delete()
    return redirect('/teams/' + team.name + '/')
    
@login_needed_and_post_method
def decline_invite_api(req, name):
    sender = User.objects.filter(name=name).first()
    if not sender:
        return HttpResponseNotFound('Пользователя не найдено')
    
    invite = Invite.objects.filter(sender=sender, receiver=req.user).first()
    if not invite:
        return HttpResponseNotFound('Приглашения не найдено')
    
    invite.delete()
    return HttpResponse('Вы отклонили приглашение')

@login_needed_and_post_method
def decline_request_api(req, name):
    sender = User.objects.filter(name=name).first()
    if not sender:
        return HttpResponseNotFound('Пользователя не существует')
    
    request = Request.objects.filter(sender=sender, receiver=req.user)
    if not request:
        return HttpResponseNotFound('Запрос не найден')
    
    request.delete()
    return HttpResponse('Вы отклонили запрос')

@login_needed_and_post_method
def create_team_ad_api(req):
    project = req.POST['project']
    role = req.POST['role']
    skills = req.POST['skills']

    user = req.user
    team = Team.objects.filter(owner=user).first()
    if not team:
        return HttpResponseNotFound('Вы не являетесь владельцем команды')
    
    ad = TeamAd.objects.filter(team=team).first()
    if ad:
        change_Ad(ad=ad, project=project, role=role, skills=skills)

    else:
        TeamAd.objects.create(team=team, project=project, role=role, skills=skills)
    
    return redirect('/teams/' + team.name + '/')

@login_needed_and_post_method
def create_user_ad_api(req):
    project = req.POST['project']
    role = req.POST['role']
    skills = req.POST['skills']

    user = req.user
    membership = TeamMembership.objects.filter(user=user).first()
    if membership:
        return HttpResponseBadRequest('Вы состоите в команде. Выйдите из команды чтобы создать анкету')
    
    ad = UserAd.objects.filter(user=user).first()
    if ad:
        change_Ad(ad=ad, project=project, role=role, skills=skills)

    else:
        UserAd.objects.create(user=user, project=project, role=role, skills=skills)

    return redirect('/users/' + user.name + '/')

@login_needed_and_post_method
def delete_team_ad_api(req): 
    user = req.user
    team = Team.objects.filter(owner=user).first()
    if not team:
        return HttpResponseNotFound('Вы не являетесь владельцем команды')
    
    ad = TeamAd.objects.filter(team=team).first()
    if not ad:
        return HttpResponseNotFound('Анкета не найдена')
    
    ad.delete()
    return redirect('/teams/' + team.name + '/')

@login_needed_and_post_method
def delete_user_ad_api(req):
    user = req.user
    
    ad = UserAd.objects.filter(user=user).first()
    if not ad:
        return HttpResponseNotFound('Анкета не найдена')
    
    ad.delete()
    return redirect('/users/' + user.name + '/')