from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.contrib import messages
from .models import Coach, CoachComment

# Create your views here.
def all_coaches_view(request:HttpRequest):
    coaches= Coach.objects.all()


    return render(request,"coaches/all_coaches.html",{"coaches":coaches})

def profile_coach_view(request:HttpRequest, coach_id:int):
    coach=Coach.objects.get(pk=coach_id)
    return render(request,"coaches/profile_coach.html", {"coach":coach})

def add_comment_view(request:HttpRequest, coach_id):
    if not request.user.is_authenticated:
        messages.error(request, "يمكن فقط للمستخدمين المسجلين إضافة تعليقات", "alert-danger")
        return redirect("accounts:signin_view")
    if request.method== "POST":
        coach_object = Coach.objects.get(pk=coach_id)
        new_comment = CoachComment(coach=coach_object,user=request.user,comment=request.POST["comment"],type=request.POST["type"], rating=request.POST["rating"])
        new_comment.save()
        messages.success(request, "تم إضافة تعليق بنجاح","alert-success")
    return redirect("coaches:profile_coach_view",coach_id=coach_id)

