from django.test import TestCase
from ..models import *

class TestTeamAd(TestCase):
    def registerOtherTeam(self):
        u = User.objects.create(name='vlad2')
        t = Team.objects.create(name='vlad2', owner=u, info='')
        TeamMembership.objects.create(user=u, team=t)
        return u, t
    
    def test_create_ad_unauthorized(self):
        resp = self.client.post('/api/createteamad', data={
            'project': 'project',
            'role': 'role',
            'skills': 'skills'
        })

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(TeamAd.objects.count(), 0)

    def test_create_ad_not_member(self):
        user = User.objects.create(name='vlad')
        self.client.force_login(user)

        resp = self.client.post('/api/createteamad', data={
            'project': 'project',
            'role': 'role',
            'skills': 'skills',
        })

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamAd.objects.count(), 0)

    def test_create_ad_not_owner(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad')
        TeamMembership.objects.create(team=t, user=user)
        self.client.force_login(user)
        
        resp = self.client.post('/api/createteamad', data={
            'project': 'project',
            'role': 'role',
            'skills': 'skills',
        })

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamAd.objects.count(), 0)

    def test_create_ad_owner(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)

        resp = self.client.post('/api/createteamad', data={
            'project': 'project',
            'role': 'role',
            'skills': 'skills'
        })

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(TeamAd.objects.count(), 1)
        teamAd = TeamAd.objects.get(team=t)
        self.assertEqual(teamAd.project, 'project')
        self.assertEqual(teamAd.skills, 'skills')
        self.assertEqual(teamAd.role, 'role')

    def test_delete_ad_no_ad(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)

        resp = self.client.post('/api/deleteteamad')

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(TeamAd.objects.count(), 0)

    def test_delete_ad_has_ad(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)
        
        TeamAd.objects.create(
            team=t,
            project='project',
            skills='skills',
            role='role'
        )

        resp = self.client.post('/api/deleteteamad')

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(TeamAd.objects.count(), 0)

    def test_create_ad_has_ad(self):
        u, t = self.registerOtherTeam()
        self.client.force_login(u)

        TeamAd.objects.create(
            team=t,
            project='project',
            skills='skills',
            role='role'
        )

        resp = self.client.post('/api/createteamad', data={
            'project': 'project2',
            'role': 'role2',
            'skills': 'skills2'
        })

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(TeamAd.objects.count(), 1)
        teamAd = TeamAd.objects.get(team=t)
        self.assertEqual(teamAd.project, 'project2')
        self.assertEqual(teamAd.skills, 'skills2')
        self.assertEqual(teamAd.role, 'role2')