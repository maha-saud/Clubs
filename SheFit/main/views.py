from django.shortcuts import render,redirect
from django.http import HttpRequest
from gyms.models import Gym
from coaches.models import Coach
from django.db.models import Avg, Q, Count
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
from .forms import ContactForm

# Create your views here.


def home_view(request:HttpRequest):
    #top_gyms = Gym.objects.annotate(avg_rating=Avg("comments__rating")).order_by("-avg_rating")[:3]
    top_gyms = (
    Gym.objects
        .annotate(
            avg_rating=Avg("comments__rating"),
            comments_count=Count("comments", filter=Q(comments__parent__isnull=True))
        )
        .order_by("-avg_rating")[:3]
)
    top_coaches= Coach.objects.all().annotate(avg_rating=Avg("coachcomment__rating")).order_by("-avg_rating")[:3]

    return render(request, "main/home.html", {"top_gyms": top_gyms, "top_coaches":top_coaches})


def about_view(request:HttpRequest):
    return render(request, "main/about.html")



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
    
    if "search" in request.GET and len(request.GET["search"])>= 1:
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

        # Pagination
        paginator = Paginator(list(gyms)+list(coaches), 6)
        page_number = request.GET.get("page", 1)
        search_page = paginator.get_page(page_number)
    else:
        search_page=None
            

    return render(request, "main/search.html" ,{"gyms":gyms,"coaches":coaches, "total_count":total_count,"results":search_page})


def contact_view(request:HttpRequest):
    if request.method=="POST":
        contact_form=ContactForm(request.POST)
        if contact_form.is_valid():
            new_msg = contact_form.save()

            content_html=render_to_string("main/mail/confirmation.html")     
            send_to= new_msg.email
            email_message=EmailMessage("confiramation", content_html,settings.EMAIL_HOST_USER,[send_to] )
            email_message.content_subtype="html"
            email_message.send()
            messages.success(request,"تم استلام رسالتك. شكرًا لك.", "alert-success")
            return redirect('main:home_view')
        else:
            print("not valid form")
    else:
        contact_form =ContactForm()        

    return render(request,"main/contact.html",{"form":contact_form}) 