from django import forms
from .models import Gym, GymComment


class GymForm(forms.ModelForm):
    class Meta:
        model = Gym
        fields = "__all__"
        widgets = {
            'about': forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            'hoods': forms.SelectMultiple(attrs={"class": "form-control"}),
            'image': forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

class GymCommentForm(forms.ModelForm):
    class Meta:
        model = GymComment
        fields = "__all__"
        widgets = {
            'comment': forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            'rating': forms.NumberInput(attrs={"class": "form-control"}),
            'comment_type': forms.Select(attrs={"class": "form-control"}),
        }
