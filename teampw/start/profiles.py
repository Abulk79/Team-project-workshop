from django.shortcuts import render, redirect
from . import models
from django.http import HttpResponse

def team(req, name):
    context = {}

    members = models.TeamMembership.objects.filter(team=name).values_list('user', flat=True)
    team = models.Team.objects.get(name=name)
    ad = models.TeamAd.objects.filter(team=name).first()

    context['members'] = members
    context['owner'] = req.user.is_authenticated and req.user.name == team.owner.name
    context['team'] = team
    context['ad'] = ad

    return render(req, 'team.html', context)

def user(req, name):
    context = {}

    user = models.User.objects.get(name=name)
    team = models.TeamMembership.objects.filter(user=user).first()
    ad = models.UserAd.objects.filter(user=user).first()

    context['user'] = user
    context['team'] = team.team if team else None
    context['ad'] = ad
    context['owner'] = req.user.is_authenticated and req.user.name == user.name

    if req.user.is_authenticated and req.user == user:
        invites = models.Invite.objects.filter(receiver=req.user)
        context['invites'] = invites

        requests = models.Request.objects.filter(receiver=req.user)
        context['requests'] = requests

    if req.user.is_authenticated:
        teamguest = models.Team.objects.filter(owner=req.user).first()
        userMembership = models.TeamMembership.objects.filter(user=user).first()
        if teamguest:
            membernames = models.TeamMembership.objects.filter(team=teamguest).values_list('user', flat=True)
            context['canInvite'] = name not in membernames
            context['canKick'] = name in membernames

    return render(req, 'user.html', context)

def changeuserinfo_api(req):
    if not req.user.is_authenticated:
        return HttpResponse('Вы не авторизованы')
    
    info = req.POST['info']
    contacts = req.POST['contacts']

    seeks = req.POST.get('seeks', 'off') == 'on'
    project = req.POST['project']
    role = req.POST['role']
    skills = req.POST['skills']

    user = req.user
    user.info = info
    user.contacts = contacts
    user.save()

    ad = models.UserAd.objects.filter(user=req.user).first()
    if seeks:
        if ad:
            changeAd(ad, project, role, skills)
        else:
            models.UserAd.objects.create(user=req.user, project=project, role=role, skills=skills)
    elif ad:
        ad.delete()

    return redirect('/users/' + req.user.name + '/')

def changeteaminfo_api(req):
    if not req.user.is_authenticated:
        return HttpResponse('Вы не авторизованы')
    
    team = models.Team.objects.get(owner=req.user)

    info = req.POST['info']
    seek = req.POST.get('seek', 'off') == 'on'
    project = req.POST['project']
    role = req.POST['role']
    skills = req.POST['skills']

    team.info = info
    team.save()

    ad = models.TeamAd.objects.filter(team=team).first()
    if seek:
        if ad:
            changeAd(ad, project, role, skills)
        else:
            models.TeamAd.objects.create(team=team, project=project, role=role, skills=skills)
    elif ad:
        ad.delete()

    return redirect('/teams/' + team.name + '/')

def invite_api(req, name):
    if not req.user.is_authenticated:
        return HttpResponse('Вы не авторизованы')
    
    team = models.Team.objects.get(owner=req.user)
    receiver = models.User.objects.get(name=name)
    sender = req.user

    if models.TeamMembership.objects.filter(user=receiver).exists():
        return HttpResponse('Пользователь уже состоит в команде')

    if models.Invite.objects.filter(team=team, sender=req.user, receiver=name).exists():
        return HttpResponse('Вы уже отправили приглашение')

    # Если запрос есть, человек вступает в команду
    request = models.Request.objects.filter(team=team, sender=receiver, receiver=sender).first()
    if request:
        request.delete()

        userad = models.UserAd.objects.filter(user=receiver).first()
        if userad:
            userad.delete()

        models.Invite.objects.filter(receiver=receiver).delete()
        models.Request.objects.filter(sender=receiver).delete()

        models.TeamMembership.objects.create(team=team, user=receiver)
        return redirect('/teams/' + team.name + '/')

    models.Invite.objects.create(team=team, sender=sender, receiver=receiver)
    return HttpResponse('Вы успешно отправили приглашение на вступление в команду')

def request_api(req, name):
    if not req.user.is_authenticated:
        return HttpResponse('Вы не авторизованы')

    sender = req.user
    receiver = models.User.objects.get(name=name)
    team = models.Team.objects.get(owner=receiver)
    
    if models.TeamMembership.objects.filter(user=sender).exists():
        return HttpResponse('Вы и так состоите в команде')
    
    if models.Request.objects.filter(team=team, sender=sender, receiver=receiver).exists():
        return HttpResponse('Вы уже отправили запрос')

    invite = models.Invite.objects.filter(team=team, sender=receiver, receiver=sender)

    # Если приглашение есть, то вступаем в команду
    if invite:
        invite.delete()
        
        userad = models.UserAd.objects.filter(user=sender).first()
        if userad:
            userad.delete()

        models.Invite.objects.filter(receiver=receiver).delete()
        models.Request.objects.filter(sender=receiver).delete()

        models.TeamMembership.objects.create(team=team, user=sender)
        return redirect('/teams/' + team.name + '/')

    models.Request.objects.create(team=team, sender=sender, receiver=receiver)
    return HttpResponse('Вы успешно отправили запрос на вступление в команду')

def leave_api(req):
    if not req.user.is_authenticated:
        return HttpResponse('Вы не авторизованы')
    
    team = models.Team.objects.filter(owner=req.user).first()
    if team:
        team.delete()
        return redirect('/')

    membership = models.TeamMembership.objects.get(user=req.user)
    membership.delete()
    return redirect('/')

def kick_api(req, name):
    if not req.user.is_authenticated:
        return HttpResponse('Вы не авторизованы')
    if req.user.name == name:
        return HttpResponse('Вы не можете выгнать самого себя')

    team = models.Team.objects.get(owner=req.user)
    membership = models.TeamMembership.objects.get(team=team, user=name)
    membership.delete()
    return redirect('/teams/' + team.name + '/')

def declineinvite_api(req, name):
    if not req.user.is_authenticated:
        return HttpResponse('Вы не авторизованы')

    sender = models.User.objects.get(name=name)
    invite = models.Invite.objects.get(sender=sender, receiver=req.user)
    invite.delete()
    return HttpResponse('Вы отклонили приглашение')

def declinerequest_api(req, name):
    if not req.user.is_authenticated:
        return HttpResponse('Вы не авторизованы')

    sender = models.User.objects.get(name=name)
    request = models.Request.objects.get(sender=sender, receiver=req.user)
    request.delete()
    return HttpResponse('Вы отклонили запрос')

def changeAd(ad, project, role, skills):
    ad.project = project
    ad.role = role
    ad.skills = skills
    ad.save()