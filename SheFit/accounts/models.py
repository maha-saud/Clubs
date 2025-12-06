from django.db import models
from django.contrib.auth.models import User
from gyms.models import Gym

# Create your models here.

class Trainee(models.Model):
    GOAL_CHOICES = [
        ('lose','إنقاص الوزن'),
        ('gain', 'زيادة الوزن'),
        ('maintain', 'المحافظة على الوزن')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="trainee")
    age =models.PositiveIntegerField()
    height =models.FloatField()
    weight =models.FloatField()
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES)
    avatar =models.ImageField(upload_to="images/" ,default='avatars/default.png')

    favorite_coaches = models.ManyToManyField("coaches.Coach", related_name="favorited_by",blank=True)
    favorite_gyms = models.ManyToManyField(Gym, related_name="favorited_by",blank=True)
    
    

    def __str__(self):
        return f"{self.user.username} - {self.get_goal_display()}"


