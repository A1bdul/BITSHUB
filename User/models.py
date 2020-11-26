from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    About = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_male = models.BooleanField(default=True)
    facebook = models.CharField(blank=True, max_length=100)
    twitter = models.CharField(blank=True, max_length=100)
    instagram = models.CharField(blank=True, max_length=100)
    google_plus = models.CharField(blank=True, max_length=100)
    country = models.CharField(max_length=120, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return "Profile of user {}".format(self.user.username)
