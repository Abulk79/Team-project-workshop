from django.urls import path
from . import registering, seeking, profiles, registering_api, profiles_api

urlpatterns = [
    path('', registering.home),
    path('registeraccount/', registering.register_account),
    path('login/', registering.login_account),
    path('registerteam/', registering.register_team),

    path('api/verifyemail', registering_api.verify_email_api),
    path('api/registeraccount', registering_api.register_account_api),
    path('api/login', registering_api.login_api),
    path('api/registerteam', registering_api.register_team_api),
    path('api/logout', registering_api.logout_api),
] + [
    path('seekteam/', seeking.seek_team),
    path('seekers/', seeking.seekers),
] + [
    path('teams/<str:name>/', profiles.team),
    path('users/<str:name>/', profiles.user),

    path('api/changeuserinfo', profiles_api.change_user_info_api),
    path('api/changeteaminfo', profiles_api.change_team_info_api),
    path('api/createteamad', profiles_api.create_team_ad_api),
    path('api/createuserad', profiles_api.create_user_ad_api),
    path('api/deleteteamad', profiles_api.delete_team_ad_api),
    path('api/deleteuserad', profiles_api.delete_user_ad_api),
    path('api/invite/<str:name>', profiles_api.invite_api),
    path('api/request/<str:name>', profiles_api.request_api),
    path('api/declinerequest/<str:name>', profiles_api.decline_request_api),
    path('api/declineinvite/<str:name>', profiles_api.decline_invite_api),
    path('api/leave', profiles_api.leave_api),
    path('api/kick/<str:name>', profiles_api.kick_api),
]