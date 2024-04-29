from django.test import TestCase
from ..models import *

class TeamTest(TestCase):
    def loginUser(self):
        user = User.objects.create(name='vlad')
        self.client.force_login(user)
        return user
    
    def registerOtherTeam(self):
        u = User.objects.create(name='vlad2')
        t = Team.objects.create(name='vlad2', owner=u, info='info')
        TeamMembership.objects.create(user=u, team=t)
        return u, t

    def test_register_team_unauthorized(self):
        resp = self.client.post('/api/registerteam', data={
            'name': 'team',
            'info': 'info',
        })

        self.assertEqual(resp.status_code, 403)

    def test_register_team(self): 
        user = self.loginUser()

        resp = self.client.post('/api/registerteam', data={
            'name': 'TEam-_123',
            'info': 'info',
        })

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamMembership.objects.count(), 1)

        team = Team.objects.get(name='TEam-_123')
        self.assertEqual(team.owner, user)
        self.assertEqual(team.info, 'info')

        membership = TeamMembership.objects.get(user=user)
        self.assertEqual(membership.team, team)

    def test_invalid_name(self):
        self.loginUser()

        resp = self.client.post('/api/registerteam', data={
            'name': 'TEam&%',
            'info': 'info',
        })

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Team.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 0)

    def test_short_name(self):
        self.loginUser()

        resp = self.client.post('/api/registerteam', data={
            'name': '-_',
            'info': 'info',
        })

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Team.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 0)

    def test_name_exists(self):
        self.loginUser()
        u, t = self.registerOtherTeam()

        resp = self.client.post('/api/registerteam', data={
            'name': 'vlad2',
            'info': 'info2'
        })

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(TeamMembership.objects.count(), 1)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(Team.objects.get(name='vlad2').owner, u)
        self.assertEqual(User.objects.count(), 2)
        team = Team.objects.get(name='vlad2')
        self.assertEqual(team.owner, u)
        self.assertEqual(team.info, 'info')     

    def test_has_team(self):
        user = self.loginUser()
        u, t = self.registerOtherTeam()
        TeamMembership.objects.create(user=user, team=t)

        resp = self.client.post('/api/registerteam', data={
            'name': 'team2',
            'info': 'info2',
        })

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamMembership.objects.count(), 2)

    def test_change_team_info(self):
        user = self.loginUser()
        self.client.post('/api/registerteam', data={
            'name': 'team',
            'info': 'info'
        })

        team = Team.objects.get(name='team')

        resp = self.client.post('/api/changeteaminfo', data={'info': 'info2',})

        team = Team.objects.get(name='team')

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(team.owner, user)
        self.assertEqual(team.info, 'info2')
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamMembership.objects.count(), 1)
        self.assertEqual(TeamAd.objects.count(), 0)

    def test_change_team_info_not_owner(self):
        user = self.loginUser()
        u, t = self.registerOtherTeam()
        TeamMembership.objects.create(user=user, team=t)

        resp = self.client.post('/api/changeteaminfo', data={'info': 'info2',})

        team = Team.objects.get(name='vlad2')

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(team.owner, u)
        self.assertEqual(team.info, 'info')
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamMembership.objects.count(), 2)
        self.assertEqual(TeamAd.objects.count(), 0)

    def test_change_team_info_unauthorized(self):
        self.registerOtherTeam()

        resp = self.client.post('/api/changeteaminfo', data={'info': 'info2',})

        self.assertEqual(resp.status_code, 403)
        team = Team.objects.get(name='vlad2')
        self.assertEqual(team.info, 'info')
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamMembership.objects.count(), 1)

    def test_team_owner_leave(self):
        self.loginUser()
        resp = self.client.post('/api/registerteam', data={
            'name': 'team',
            'info': 'info'
        })

        team = Team.objects.get(name='team')
        user = User.objects.create(name='vlad3')
        TeamMembership.objects.create(team=team, user=user)

        TeamAd.objects.create(
            team=team,
            project='project',
            role='role',
            skills='skills'
        )

        self.assertEqual(resp.status_code, 302)
        self.client.post('/api/leave', data={})
        self.assertEqual(Team.objects.count(), 0)
        self.assertEqual(TeamMembership.objects.count(), 0)
        self.assertEqual(TeamAd.objects.count(), 0)
        