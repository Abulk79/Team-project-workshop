from django.test import TestCase
from ..models import *

class TestTeamAd(TestCase):
    def registerOtherTeam(self):
        u = User.objects.create(name='vlad2')
        t = Team.objects.create(name='vlad2', owner=u, info='')
        TeamMembership.objects.create(user=u, team=t)
        return u, t
    
    def test_create_ad_unauthorized(self):
        resp = self.client.post('/api/createuserad', data={
            'project': 'project',
            'role': 'role',
            'skills': 'skills'
        })

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(UserAd.objects.count(), 0)

    def test_create_ad_authorized(self):
        user = User.objects.create(name='vlad')
        self.client.force_login(user)

        resp = self.client.post('/api/createuserad', data={
            'project': 'project',
            'role': 'role',
            'skills': 'skills'
        })

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(UserAd.objects.count(), 1)
        userAd = UserAd.objects.get(user=user)
        self.assertEqual(userAd.project, 'project')
        self.assertEqual(userAd.skills, 'skills')
        self.assertEqual(userAd.role, 'role')

    def test_delete_ad_no_ad(self):
        user = User.objects.create(name='vlad')
        self.client.force_login(user)

        resp = self.client.post('/api/deleteuserad')

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(UserAd.objects.count(), 0)

    def test_delete_ad_has_ad(self):
        user = User.objects.create(name='vlad')
        self.client.force_login(user)
        
        UserAd.objects.create(
            user=user,
            project='project',
            skills='skills',
            role='role'
        )

        resp = self.client.post('/api/deleteuserad')

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(UserAd.objects.count(), 0)

    def test_create_ad_has_ad(self):
        user = User.objects.create(name='vlad')
        self.client.force_login(user)

        UserAd.objects.create(
            user=user,
            project='project',
            skills='skills',
            role='role'
        )

        resp = self.client.post('/api/createuserad', data={
            'project': 'project2',
            'role': 'role2',
            'skills': 'skills2'
        })

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(UserAd.objects.count(), 1)
        userAd = UserAd.objects.get(user=user)
        self.assertEqual(userAd.project, 'project2')
        self.assertEqual(userAd.skills, 'skills2')
        self.assertEqual(userAd.role, 'role2')

    def test_create_user_ad_in_team(self):
        u, t = self.registerOtherTeam()
        user = User.objects.create(name='vlad3')
        TeamMembership.objects.create(user=user, team=t)
        self.client.force_login(user)

        resp = self.client.post('/api/createuserad', data={
            'project': 'project',
            'role': 'role',
            'skills': 'skills',
        })

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(UserAd.objects.count(), 0)