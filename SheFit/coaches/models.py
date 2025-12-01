from django.db import models
from django.contrib.auth.models import User
from gyms.models import Gym


# Create your models here.
class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="coach")

    speciality = models.TextField()
    experience_years = models.IntegerField()
    phone = models.CharField(max_length=10)
    gym = models.ForeignKey(Gym, on_delete=models.SET_NULL, null=True, blank=True, related_name="coaches")
    avatar =models.ImageField(upload_to="images/" ,default='avatars/default.png')

    def __str__(self):
        return self.user.username

 