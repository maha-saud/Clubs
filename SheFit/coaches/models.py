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
    
class CoachComment(models.Model):
    class RatingChoices(models.IntegerChoices):
        STAR1 = 1, "One Star"
        STAR2 = 2, "Two Stars"
        STAR3 = 3, "Three Stars"
        STAR4 = 4, "Four Stars"
        STAR5 = 5, "Five Stars"

    TYPE_COMMENT = [
        ('inquiry','استفسار'),
        ('previous_member', 'مشترك سابق')
    ]  
    coach=models.ForeignKey(Coach, on_delete=models.CASCADE)
    user =models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_COMMENT ,default='inquiry')
    comment= models.TextField()
    rating = models.SmallIntegerField(choices=RatingChoices.choices ,default=RatingChoices.STAR5)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} on {self.Coach.user.username}"    

 