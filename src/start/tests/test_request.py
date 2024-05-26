from django.test import TestCase
from ..models import *

class TestInvite(TestCase):
    def registerOtherTeam(self):
        u = User.objects.create(name='vlad2')
        t = Team.objects.create(name='vlad2', owner=u, info='info')
        TeamMembership.objects.create(user=u, team=t)
        return u, t

    def test_send_request_unauthorized(self):
        u, t = self.registerOtherTeam()
        resp = self.client.post('/api/request/vlad2')
        
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(Invite.objects.count(), 0)

    def test_send_request_no_team_receiver(self):
        user = User.objects.create(name='vlad')
        User.objects.create(name='vlad2')
        self.client.force_login(user)

        resp = self.client.post('/api/request/vlad2')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamMembership.objects.count(), 0)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)

    def test_send_request_to_member_not_owner(self):
        u, t = self.registerOtherTeam()
        other = User.objects.create(name='vlad3')
        user = User.objects.create(name='vlad4')
        TeamMembership.objects.create(user=other, team=t)
        self.client.force_login(user)

        resp = self.client.post('/api/request/vlad3')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamMembership.objects.count(), 2)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)

    def test_send_request(self):
        self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        self.client.force_login(user)

        resp = self.client.post('/api/request/vlad2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(TeamMembership.objects.count(), 1)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 1)

    def test_send_request_user_not_exists(self):
        user = User.objects.create(name='vlad3')
        self.client.force_login(user)

        resp = self.client.post('/api/request/vlad4')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamMembership.objects.count(), 0)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)

    def test_send_request_has_request(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        self.client.force_login(user)
        Request.objects.create(team=t, receiver=u, sender=user)

        resp = self.client.post('/api/request/vlad2')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(TeamMembership.objects.count(), 1)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 1)

    def test_send_request_has_invite(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        self.client.force_login(user)
        Invite.objects.create(team=t, receiver=user, sender=u)

        resp = self.client.post('/api/request/vlad2')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(TeamMembership.objects.count(), 2)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.filter(user=user, team=t).exists(), True)

    def test_decline_request(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        self.client.force_login(u)
        Request.objects.create(team=t, receiver=u, sender=user)

        resp = self.client.post('/api/declinerequest/vlad3')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(TeamMembership.objects.count(), 1)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)

    def test_decline_request_unauthorized(self):
        resp = self.client.post('/api/declinerequest/vlad2')
        self.assertEqual(resp.status_code, 403)

    def test_decline_request_no_user(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)

        resp = self.client.post('/api/declinerequest/vladdd')
        self.assertEqual(resp.status_code, 404)

    def test_decline_request_has_invite(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        Invite.objects.create(receiver=user, sender=u, team=t)
        self.client.force_login(u)

        resp = self.client.post('/api/declinerequest/vlad3')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamMembership.objects.count(), 1)
        self.assertEqual(Invite.objects.count(), 1)
        self.assertEqual(Request.objects.count(), 0)

    def test_decline_request_no_request(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        self.client.force_login(u)

        resp = self.client.post('/api/declinerequest/vlad3')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamMembership.objects.count(), 1)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)

    def test_send_request_already_in_team(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        team = Team.objects.create(name='vlad3', owner=user)
        TeamMembership.objects.create(team=team, user=user)
        self.client.force_login(u)

        resp = self.client.post('/api/request/vlad3')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(TeamMembership.objects.count(), 2)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)

    def test_accept_invite_delete_other(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        Invite.objects.create(team=t, sender=u, receiver=user)
        UserAd.objects.create(
            user=user, 
            role='role', 
            project='project', 
            skills='skills'
        )

        otherUser1 = User.objects.create(name='vlad4')
        otherTeam1 = Team.objects.create(name='vlad4', owner=otherUser1, info='info')
        TeamMembership.objects.create(user=otherUser1, team=otherTeam1)
        otherUser2 = User.objects.create(name='vlad5')
        otherTeam2 = Team.objects.create(name='vlad5', owner=otherUser2, info='info')
        TeamMembership.objects.create(user=otherUser2, team=otherTeam2)
        Invite.objects.create(team=otherTeam1, sender=otherUser1, receiver=user)
        Request.objects.create(team=otherTeam2, sender=user, receiver=otherUser2)
        self.client.force_login(user)

        resp = self.client.post('/api/request/vlad2')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 4)
        self.assertEqual(UserAd.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.filter(user=user, team=t).exists(), True)