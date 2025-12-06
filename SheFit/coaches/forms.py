from django import forms
from .models import Coach, CoachComment, SubscriptionPlan, Post


class CoachForm(forms.ModelForm):
    class Meta:
        model = Coach
        fields = "__all__"


class CoachCommentForm(forms.ModelForm):
    class Meta:
        model = CoachComment
        fields = "__all__"
       

class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = ['name','description','duration_days', 'price', 'max_subscribers']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "img"]
           
