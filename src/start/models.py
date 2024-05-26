from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser

class CustomUserManager(UserManager):
    def create_user(self, name, email, password,):
        user = self.model(name=name, email=email, password=password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    name = models.CharField(max_length=255, primary_key=True)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    
    info = models.CharField(max_length=4095, default='')
    contacts = models.CharField(max_length=255, default='')

    objects = CustomUserManager()

    USERNAME_FIELD = 'name'

class UnverifiedUser(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    code = models.CharField(max_length=128)

class Team(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    info = models.CharField(max_length=4095)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

class TeamAd(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    project = models.CharField(max_length=1023)
    role = models.CharField(max_length=1023)
    skills = models.CharField(max_length=2047, default='')

class UserAd(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    project = models.CharField(max_length=1023)
    role = models.CharField(max_length=1023)
    skills = models.CharField(max_length=2047)

class Invite(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invite_sender_foreign_key')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invite_receiver_foreign_key')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

class Request(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_sender_foreign_key')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_receiver_foreign_key')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)