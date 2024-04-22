from django.shortcuts import render
from . import models

def seekteam(req):
    context = {}

    ads = models.TeamAd.objects.all()
    context['ads'] = ads

    return render(req, 'seekteam.html', context)

def seekers(req):
    context = {}

    ads = models.UserAd.objects.all()
    context['ads'] = ads

    return render(req, 'seekers.html', context)