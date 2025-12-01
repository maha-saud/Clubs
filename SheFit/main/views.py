from django.shortcuts import render,redirect
from django.http import HttpRequest
# Create your views here.

def home_view(request:HttpRequest):

    return render(request,"main/home.html")

def mode_view(request:HttpRequest,mode):
    res=redirect(request.GET.get("next","/"))# "/": for defult query
    if mode=="light":
        res.set_cookie("mode","light")
    elif mode=="dark":
        res.set_cookie("mode","dark")
    return res
