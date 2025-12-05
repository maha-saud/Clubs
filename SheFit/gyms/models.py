from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Hood(models.Model):

    name =models.CharField(max_length=2048)
    
    
    def __str__(self) -> str:
        return self.name

class Gym(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="gym", null=True, blank=True)
    name =models.CharField(max_length=2048 ,default="")
    image =models.ImageField(upload_to="images/", default='avatars/default.png')
    hoods =models.ManyToManyField(Hood)
    has_coach=models.BooleanField(default=True)
    about =models.TextField()
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2)  # سعر اشتراك شهري
    website = models.URLField(max_length=300, null=True, blank=True) # رابط ال website الخاص للنادي نفسه اذا كان عندهم 

    def __str__(self) -> str:
        return self.user.username if self.user else "Gym"   


class GymComment(models.Model):

    class CommentType(models.TextChoices):
        MEMBER = "member", "مشترك"
        VISITOR = "visitor", "زائر"
        QUESTION = "question", "استفسار"

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="written_comments") # لازم اعطي اسم لان استخدمت المودل مرتينfk
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies") # هذي عشان اربط الردود في بعض
    reply_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="mentioned_in_comments")  # fk مره ثانيه ,الشخص اللي تردين عليه مباشرة
    comment_type = models.CharField(max_length=20, choices=CommentType.choices, null=True, blank=True) # عشان نوع التعليق بالردود يكون فاضي
    rating = models.SmallIntegerField(null=True, blank=True) # عشان ما يطلع تقييم للردود 
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} on {self.gym}"
