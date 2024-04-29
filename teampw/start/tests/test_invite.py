from django.test import TestCase
from ..models import *

class TestInvite(TestCase):
    def registerOtherTeam(self):
        u = User.objects.create(name='vlad2')
        t = Team.objects.create(name='vlad2', owner=u, info='info')
        TeamMembership.objects.create(user=u, team=t)
        return u, t

    def test_send_invite_unauthorized(self):
        User.objects.create(name='vlad')
        resp = self.client.post('/api/invite/vlad')
        
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)

    def test_send_invite_no_team_sender(self):
        user = User.objects.create(name='vlad')
        User.objects.create(name='vlad2')
        self.client.force_login(user)

        resp = self.client.post('/api/invite/vlad2')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamMembership.objects.count(), 0)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)

    def test_send_invite_not_owner(self):
        user = User.objects.create(name='vlad')
        self.client.force_login(user)
        u, t = self.registerOtherTeam()
        User.objects.create(name='vlad3')
        TeamMembership.objects.create(user=user, team=t)

        resp = self.client.post('/api/invite/vlad3', data={})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 2)

    def test_send_invite(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)
        other = User.objects.create(name='vlad3')

        resp = self.client.post('/api/invite/vlad3')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Invite.objects.count(), 1)
        self.assertEqual(Invite.objects.filter(team=t, sender=u, receiver=other).exists(), True)

    def test_send_invite_not_exists(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)

        resp = self.client.post('/api/invite/vladdd')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 1)

    def test_send_invite_to_member(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)
        other = User.objects.create(name='vlad3')
        TeamMembership.objects.create(user=other, team=t)

        resp = self.client.post('/api/invite/vlad3', data={})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 2)

    def test_send_invite_has_request(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)
        other = User.objects.create(name='vlad3')
        Request.objects.create(team=t, sender=other, receiver=u)

        resp = self.client.post('/api/invite/vlad3')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 2)

    def test_send_invite_has_invite(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)
        other = User.objects.create(name='vlad3')
        Invite.objects.create(team=t, sender=u, receiver=other)

        resp = self.client.post('/api/invite/vlad3')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Invite.objects.count(), 1)
        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 1)

    def test_decline_invite(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        Invite.objects.create(team=t, sender=u, receiver=user)
        self.client.force_login(user)
        
        resp = self.client.post('/api/declineinvite/vlad2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 1)

    def test_decline_invite_unauthorized(self):
        resp = self.client.post('/api/declineinvite/vlad2')
        self.assertEqual(resp.status_code, 403)

    def test_decline_invite_no_user(self):
        user = User.objects.create(name='vlad3')
        self.client.force_login(user)

        resp = self.client.post('/api/declineinvite/vlad4')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 0)

    def test_decline_invite_no_invite(self):
        user = User.objects.create(name='vlad3')
        self.client.force_login(user)
        other = User.objects.create(name='vlad4')

        resp = self.client.post('/api/declinveinvite/vlad4')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 0)

    def test_decline_invite_has_request(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        Request.objects.create(team=t, sender=user, receiver=u)
        self.client.force_login(user)

        resp = self.client.post('/api/declinveinvite/vlad2')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 1)
        self.assertEqual(TeamMembership.objects.count(), 1)

    def test_accept_request_delete_other(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        Request.objects.create(team=t, sender=user, receiver=u)
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

        self.client.force_login(u)
        resp = self.client.post('/api/invite/vlad3')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 4)
        self.assertEqual(UserAd.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.filter(user=user, team=t).exists(), True)