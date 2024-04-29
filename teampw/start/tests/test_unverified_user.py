from django.test import TestCase
from ..models import *
import hashlib

class UnverifiedUserTest(TestCase):
    def send_verification(self, name, email='', password=''):
        data = { 
            'name': name,
            'email': email,
            'password': password
        }

        req = self.client.post('/api/verifyemail', data=data)

        return req.status_code

    def test_unverified_account(self):
        status = self.send_verification('VLad_-123', 'vlad@mail.ru', 'pass')

        self.assertEqual(status, 200)
        self.assertEqual(UnverifiedUser.objects.count(), 1)

        unvUser = UnverifiedUser.objects.get(name='VLad_-123')

        self.assertEqual(unvUser.email, 'vlad@mail.ru')
        self.assertEqual(unvUser.password, hashlib.md5('pass'.encode()).hexdigest())


    def test_no_new_users(self):
        self.send_verification('vlad', 'vlad@mail.ru', 'pass')

        self.assertEqual(User.objects.all().count(), 0)

    def test_name_exists_unverified(self):
        status = self.send_verification('vlad', 'vlad@mail.ru', 'pass')
        self.assertEqual(status, 200)

        oldCode = UnverifiedUser.objects.get(name='vlad').code
        status2 = self.send_verification('vlad', 'vlad2@mail.ru', 'pass2')

        self.assertEqual(status2, 200)
        self.assertEqual(1, UnverifiedUser.objects.count())
        self.assertEqual(0, User.objects.count())

        user = UnverifiedUser.objects.get(name='vlad')

        self.assertEqual(user.email, 'vlad2@mail.ru')
        self.assertEqual(user.password, hashlib.md5('pass2'.encode()).hexdigest())
        self.assertNotEqual(oldCode, user.code)

    def test_name_exists_verified(self):
        User.objects.create(name='vlad')
        status = self.send_verification('vlad')
        self.assertEqual(status, 400)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UnverifiedUser.objects.count(), 0)

    def test_len_name(self):
        status = self.send_verification('v')
        self.assertEqual(status, 400)
        self.assertEqual(UnverifiedUser.objects.count(), 0)

    def test_invalid_name(self):
        status = self.send_verification('-_$#@')
        self.assertEqual(status, 400)
        self.assertEqual(UnverifiedUser.objects.count(), 0)