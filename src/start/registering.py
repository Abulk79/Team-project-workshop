from django.shortcuts import render
from .models import *

def home(req):
    context = {}
    if req.user.is_authenticated:
        user = User.objects.get(name=req.user.name)
        teamMembership = TeamMembership.objects.filter(user=req.user).first()

        if teamMembership:
            context['team'] = teamMembership.team
        context['user'] = user
    else:
        context['user'] = None

    return render(req, 'home.html', context)

def register_account(req):
    return render(req,'registeraccount.html', {})

def login_account(req):
    return render(req, 'login.html', {})

def register_team(req):
    return render(req,'registerteam.html', {})
