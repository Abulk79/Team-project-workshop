from django.shortcuts import render
from .models import *

def team(req, name):
    context = {}

    members = TeamMembership.objects.filter(team=name).values_list('user', flat=True)
    team = Team.objects.get(name=name)
    ad = TeamAd.objects.filter(team=name).first()

    context['members'] = members
    context['owner'] = req.user.is_authenticated and req.user.name == team.owner.name
    context['isMember'] = req.user.is_authenticated and req.user.name in members
    context['team'] = team
    context['ad'] = ad
    context['canRequest'] = req.user.is_authenticated and not TeamMembership.objects.filter(user=req.user).exists()

    return render(req, 'team.html', context)

def user(req, name):
    context = {}

    user = User.objects.get(name=name)
    teamMembership = TeamMembership.objects.filter(user=user).first()
    ad = UserAd.objects.filter(user=user).first()

    context['user'] = user
    context['team'] = teamMembership.team if teamMembership else None
    context['ad'] = ad
    context['owner'] = req.user.is_authenticated and req.user.name == user.name

    if req.user.is_authenticated and req.user == user:
        invites = Invite.objects.filter(receiver=req.user)
        context['invites'] = invites

        requests = Request.objects.filter(receiver=req.user)
        context['requests'] = requests

    if req.user.is_authenticated:
        teamguest = Team.objects.filter(owner=req.user).first()
        userMembership = TeamMembership.objects.filter(user=user).first()
        if teamguest:
            membernames = TeamMembership.objects.filter(team=teamguest).values_list('user', flat=True)
            context['canInvite'] = not userMembership
            context['canKick'] = name in membernames and not req.user.name == user.name

    return render(req, 'user.html', context)