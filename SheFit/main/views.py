from django.shortcuts import render,redirect
from django.http import HttpRequest
from gyms.models import Gym
from django.db.models import Avg

# Create your views here.


def home_view(request:HttpRequest):
    top_gyms = Gym.objects.annotate(avg_rating=Avg("comments__rating")).order_by("-avg_rating")[:3]

    return render(request, "main/home.html", {"top_gyms": top_gyms})



def mode_view(request:HttpRequest,mode):
    res=redirect(request.GET.get("next","/"))# "/": for defult query
    if mode=="light":
        res.set_cookie("mode","light")
    elif mode=="dark":
        res.set_cookie("mode","dark")
    return res
