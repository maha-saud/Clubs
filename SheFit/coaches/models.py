from django.db import models
from django.contrib.auth.models import User
from accounts.models import Trainee
from gyms.models import Gym
from django.utils import timezone
from datetime import timedelta

from django.core.validators import RegexValidator  # ⬅ أعلى الملف

saudi_phone_validator = RegexValidator(
    regex=r'^(05|9665|\+9665)\d{8}$',
    message="رقم الجوال غير صحيح (مثال: 05xxxxxxxx)"
)


# Create your models here.
class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="coach")

    speciality = models.TextField()
    experience_years = models.IntegerField()
    phone = models.CharField(max_length=20, validators=[saudi_phone_validator], verbose_name="رقم الجوال")    
    gym = models.ForeignKey(Gym, on_delete=models.SET_NULL, null=True, blank=True, related_name="coaches")
    avatar =models.ImageField(upload_to="images/" ,default='avatars/default.png')
    about= models.TextField(default="")
    website = models.URLField(max_length=300 , null=True, blank=True)

    def __str__(self):
        return self.user.username

class SubscriptionPlan(models.Model):
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="plans")
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_days = models.IntegerField()
    price = models.FloatField()
    max_subscribers = models.IntegerField(default=10)
    current_subscribers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.coach.user.username}"
    
    # حساب عدد المقاعد المتبقية في الباقة
    @property
    def remaining(self):
        return self.max_subscribers - self.current_subscribers


class UserSubscription(models.Model):
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name="user_subscriptions")
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        #حساب تاريخ النهاية تلقائيا
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

class CoachComment(models.Model):
    class RatingChoices(models.IntegerChoices):
        STAR1 = 1, "One Star"
        STAR2 = 2, "Two Stars"
        STAR3 = 3, "Three Stars"
        STAR4 = 4, "Four Stars"
        STAR5 = 5, "Five Stars"

    TYPE_COMMENT = [
        ('inquiry','استفسار'),
        ('previous_member', 'مشترك سابق'),
        ('current_member', 'مشترك حالي')
    ]  
    coach=models.ForeignKey(Coach, on_delete=models.CASCADE)
    user =models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_COMMENT ,default='inquiry')
    comment= models.TextField()
    rating = models.SmallIntegerField(choices=RatingChoices.choices ,default=RatingChoices.STAR5)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} on {self.coach.user.username}"   

class Post(models.Model):
        coach=models.ForeignKey(Coach, on_delete=models.CASCADE)
        title = models.CharField(max_length=200)
        content = models.TextField()
        img = models.ImageField(upload_to="images/", null=True, blank=True)
        created_at = models.DateTimeField(auto_now_add=True)
        def __str__(self):
            return self.title


 