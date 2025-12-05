from django.shortcuts import render,redirect
from django.http import HttpRequest
from gyms.models import Gym
from coaches.models import Coach
from django.db.models import Avg, Q

# Create your views here.


def home_view(request:HttpRequest):
    top_gyms = Gym.objects.annotate(avg_rating=Avg("comments__rating")).order_by("-avg_rating")[:3]
    top_coaches= Coach.objects.all().annotate(avg_rating=Avg("coachcomment__rating")).order_by("-avg_rating")[:3]

    return render(request, "main/home.html", {"top_gyms": top_gyms, "top_coaches":top_coaches})



def mode_view(request:HttpRequest):

    mode = request.COOKIES.get("mode", "light")

    new_mode = "dark" if mode == "light" else "light"
    
    res=redirect(request.GET.get("next","/"))# "/": for defult query
    res.set_cookie("mode", new_mode)
    return res

def search_view(request:HttpRequest):
    gyms=[]
    coaches= []
    total_count=0
    
    if "search" in request.GET and len(request.GET["search"])>= 3:
        gyms=Gym.objects.filter(
            Q(name__contains=request.GET["search"])|
            Q(about__contains=request.GET["search"])|
            Q(user__username__contains=request.GET["search"]) 
            )
        coaches=Coach.objects.filter(
            Q(user__username__contains=request.GET["search"]) |
            Q(user__first_name__contains=request.GET["search"]) |
            Q(user__last_name__contains=request.GET["search"]) 
            )
        total_count = gyms.count() + coaches.count()
         

    return render(request, "main/search.html" ,{"gyms":gyms,"coaches":coaches, "total_count":total_count})