from django.test import TestCase
from ..models import *

class TestTeamMembership(TestCase):
    def loginUser(self):
        user = User.objects.create(name='vlad')
        self.client.force_login(user)
        return user
    
    def registerOtherTeam(self):
        u = User.objects.create(name='vlad2')
        t = Team.objects.create(name='vlad2', owner=u, info='info')
        TeamMembership.objects.create(user=u, team=t)
        return u, t
    
    def test_leave_team_not_owner(self):
        u = User.objects.create(name='vlad2')
        t = Team.objects.create(name='vlad2', owner=u, info='info')
        TeamMembership.objects.create(user=u, team=t)
        user = User.objects.create(name='vlad')
        self.client.force_login(user)
        TeamMembership.objects.create(user=user, team=t)

        resp = self.client.post('/api/leave', data={})

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamMembership.objects.count(), 1)

    def test_leave_no_team(self):
        user = User.objects.create(name='vlad')
        self.client.force_login(user)

        resp = self.client.post('/api/leave', data={})
        self.assertEqual(resp.status_code, 404)

    def test_leave_unauthorized(self):
        resp = self.client.post('/api/leave', data={})
        self.assertEqual(resp.status_code, 403)

    def test_kick_unauthorized(self):
        resp = self.client.post('/api/kick/vlad', data={})
        self.assertEqual(resp.status_code, 403)

    def test_kick(self):
        user = User.objects.create(name='vlad')
        u, t = self.registerOtherTeam()
        self.client.force_login(u)
        Request.objects.create(sender=user, receiver=u, team=t)
        resp = self.client.post('/api/invite/vlad', data={})

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(TeamMembership.objects.count(), 2)
        membership = TeamMembership.objects.get(user=user)
        self.assertEqual(membership.team, t)
        self.assertEqual(Invite.objects.count(), 0)
        self.assertEqual(Request.objects.count(), 0)

        resp = self.client.post('/api/kick/vlad', data={})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(TeamMembership.objects.count(), 1)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamMembership.objects.filter(user=user).exists(), False)

    def test_kick_owner(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)

        resp = self.client.post('/api/kick/vlad2')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(TeamMembership.objects.count(), 1)
        self.assertEqual(Team.objects.count(), 1)

    def test_kick_has_no_team_receiver(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)
        User.objects.create(name='vlad')

        resp = self.client.post('/api/kick/vlad', data={})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(TeamMembership.objects.count(), 1)
        self.assertEqual(Team.objects.count(), 1)

    def test_kick_has_no_team_sender(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad')
        new = User.objects.create(name='vlad3')
        TeamMembership.objects.create(user=new, team=t)
        self.client.force_login(user)

        resp = self.client.post('/api/kick/vlad3', data={})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamMembership.objects.count(), 2)

    def test_kick_not_owner(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad')
        new = User.objects.create(name='vlad3')
        TeamMembership.objects.create(user=new, team=t)
        TeamMembership.objects.create(user=user, team=t)
        self.client.force_login(user)

        resp = self.client.post('/api/kick/vlad3', data={})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamMembership.objects.count(), 3)

    def test_kick_not_exists(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)

        resp = self.client.post('/api/kick/vladddd')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamMembership.objects.count(), 1)