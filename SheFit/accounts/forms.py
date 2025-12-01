from django import forms
from django.contrib.auth.models import User
from coaches.models import Coach
from .models import Trainee
from gyms.models import Gym

class CoachSignUpForm(forms.ModelForm):

    class Meta: 
        model = Coach 
        exclude = ["user"]

class TraineeSignUpForm(forms.ModelForm):

    class Meta: 
        model = Trainee 
        exclude = ["user"]

class GymSignUpForm(forms.ModelForm):

    class Meta: 
        model = Gym 
        exclude = ["user"]