from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Hood(models.Model):

    name =models.CharField(max_length=2048)
    
    
    def __str__(self) -> str:
        return self.name

class Gym(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="gym", null=True, blank=True)
    image =models.ImageField(upload_to="images/")
    hoods =models.ManyToManyField(Hood)
    has_coach=models.BooleanField(default=True)
    about =models.TextField()

    def __str__(self) -> str:
        return self.user.username if self.user else "Gym"   


class GymComment(models.Model):

    class CommentType(models.TextChoices):
        MEMBER = "member", "مشترك"
        VISITOR = "visitor", "زائر"
        QUESTION = "question", "استفسار"

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_type = models.CharField(max_length=20, choices=CommentType.choices)
    rating = models.SmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} on {self.gym}"
