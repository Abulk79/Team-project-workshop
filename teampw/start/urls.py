from django.urls import path
from . import registering, seeking, profiles

urlpatterns = [
    path('', registering.home),
    path('registeraccount/', registering.registeraccount),
    path('login/', registering.loginaccount),
    path('registerteam/', registering.registerteam),

    path('api/verifyemail', registering.verifyemail_api),
    path('api/registeraccount', registering.registeraccount_api),
    path('api/login', registering.login_api),
    path('api/registerteam', registering.registerteam_api),
    path('api/logout', registering.logout_api),
] + [
    path('seekteam/', seeking.seekteam),
    path('seekers/', seeking.seekers),
] + [
    path('teams/<str:name>/', profiles.team),
    path('users/<str:name>/', profiles.user),

    path('api/changeuserinfo', profiles.changeuserinfo_api),
    path('api/changeteaminfo', profiles.changeteaminfo_api),
    path('api/invite/<str:name>', profiles.invite_api),
    path('api/request/<str:name>', profiles.request_api),
    path('api/declinerequest/<str:name>', profiles.declinerequest_api),
    path('api/declineinvite/<str:name>', profiles.declineinvite_api),
    path('api/leave', profiles.leave_api),
    path('api/kick/<str:name>', profiles.kick_api),
]