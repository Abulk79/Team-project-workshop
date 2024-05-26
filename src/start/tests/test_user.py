from django.test import TestCase
from ..models import *
import hashlib

class UserTest(TestCase):
    def send_verification(self, name, email='', password=''):
        data = { 
            'name': name,
            'email': email,
            'password': password
        }

        resp = self.client.post('/api/verifyemail', data=data)

        return resp.status_code

    def test_verify_user(self):
        status = self.send_verification('vlad', 'vlad@mail.ru', 'pass')
        self.assertEqual(status, 200)

        code = UnverifiedUser.objects.get(name='vlad').code
        resp = self.client.get(f'/api/registeraccount?name=vlad&code={code}'.format(code=code))

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(0, UnverifiedUser.objects.count())
        self.assertEqual(1, User.objects.count())
        user = User.objects.get(name='vlad')
        self.assertEqual(user.password, hashlib.md5('pass'.encode()).hexdigest())
        self.assertEqual('vlad@mail.ru', user.email)
    
    def test_verify_wrong_code(self):
        self.send_verification('vlad')

        code = UnverifiedUser.objects.get(name='vlad').code + 'a'
        resp = self.client.get(f'/api/registeraccount?name=vlad&code={code}'.format(code=code))
        self.assertEqual(resp.status_code, 404)

        self.assertEqual(UnverifiedUser.objects.count(), 1)
        self.assertEqual(User.objects.count(), 0)

    def test_verify_wrong_name(self):
        self.send_verification('vlad')

        code = UnverifiedUser.objects.get(name='vlad').code
        resp = self.client.get(f'/api/registeraccount?name=vlad0&code={code}'.format(code=code))
        self.assertEqual(resp.status_code, 404)

        self.assertEqual(UnverifiedUser.objects.count(), 1)
        self.assertEqual(User.objects.count(), 0)

    def test_login(self):
        User.objects.create(name='vlad', password=hashlib.md5('pass'.encode()).hexdigest())
        resp = self.client.post('/api/login', {
            'name': 'vlad', 
            'password': 'pass'
        })

        self.assertEqual(resp.status_code, 302)

    def test_wrong_name(self):
        User.objects.create(name='vlad', password=hashlib.md5('pass'.encode()).hexdigest())
        resp = self.client.post('/api/login', {
            'name': 'vlad0', 
            'password': 'pass'
        })

        self.assertEqual(resp.status_code, 403)

    def test_wrong_password(self):
        User.objects.create(name='vlad', password=hashlib.md5('pass'.encode()).hexdigest())
        resp = self.client.post('/api/login', {
            'name': 'vlad', 
            'password': 'pass0'
        })

        self.assertEqual(resp.status_code, 403)
    
    def test_change_user_info_unauthorized(self):
        resp = self.client.post('/api/changeuserinfo', {
                'info': 'info',
                'contacts': 'contacts'
            }
        )

        self.assertEqual(resp.status_code, 403)

    def test_change_user_info(self):
        user = User.objects.create(name='vlad', password=hashlib.md5('vlad'.encode()).hexdigest())
        self.client.force_login(user)
        resp = self.client.post(
            '/api/changeuserinfo',{
                'info': 'info',
                'contacts': 'contacts'
            }
        )

        user = User.objects.get(name='vlad')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(user.info, 'info')
        self.assertEqual(user.contacts, 'contacts')
        self.assertEqual(UserAd.objects.count(), 0)