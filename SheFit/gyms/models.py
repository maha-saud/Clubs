from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Hood(models.Model):
    name =models.CharField(max_length=2048)
    
    
    def __str__(self):
        return self.name

class Gym(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="gym", null=True, blank=True)
    image =models.ImageField(upload_to="images/")
    hood =models.ManyToManyField(Hood)
    has_coach=models.BooleanField(default=True)
    about =models.TextField()


