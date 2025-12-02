from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.contrib import messages
from .models import Coach, CoachComment
from gyms.models import Gym
from django.db.models import Count, Avg
from django.core.paginator import Paginator

# Create your views here.
def all_coaches_view(request:HttpRequest):
    coaches= Coach.objects.all().annotate(avg_rating=Avg("coachcomment__rating"),comments_count=Count("coachcomment"))

    # فلترة التقييم
    rating_order = request.GET.get("rating", "all")
    if rating_order == "high":
        coaches = coaches.order_by("-avg_rating")
    elif rating_order == "low":
        coaches = coaches.order_by("avg_rating")

    # Pagination
    page_number = request.GET.get("page", 1)
    paginator = Paginator(coaches, 6)
    coaches_page = paginator.get_page(page_number)
    return render(request,"coaches/all_coaches.html",{"coaches":coaches,"coach_paga":coaches_page})

def profile_coach_view(request:HttpRequest, coach_id:int):
    coach=Coach.objects.get(pk=coach_id)
    related_coaches= Coach.objects.all().exclude(pk=coach_id)[0:4]
    return render(request,"coaches/profile_coach.html", {"coach":coach,"related_coaches":related_coaches})

def coach_update_view(request: HttpRequest, coach_id: int):
    try:
        coach=Coach.objects.get(pk=coach_id)
    except Coach.DoesNotExist:
        messages.error(request, "المدرب غير موجود", "alert-warning")   
         
    if request.user != coach.user:
        messages.warning(request,"فقط يمكن لصاحب الحساب التعديل","alert-warning")
        return redirect("main:home_veiw")
    
    if request.method =="POST":
        coach.speciality = request.POST.get("speciality", coach.speciality)
        coach.experience_years = request.POST.get("experience_years", coach.experience_years)
        coach.phone = request.POST.get("phone",coach.phone)

        if "avatar" in request.FILES: coach.avatar = request.FILES["avatar"]
        coach.save()
        messages.success(request,"تم تحديث بيانات المدرب بنجاح", "alert-success")
        return redirect("coaches:profile_coach_view" ,coach_id=coach.id)
    return render(request,"coaches/coach_update.html", {"coach":coach} )

def coach_delete_view(request: HttpRequest, coach_id: int):

    if not request.user.is_staff:
        messages.warning(request, "فقط يمكن لصاحب الحساب الحذف", "alert-warning")
        return redirect("main:home_view")

    try:
        coach = Coach.objects.get(pk=coach_id)
        coach.delete()
        messages.success(request, "تم حذف بنجاح", "alert-success")

    except Exception as e:
        messages.error(request, "هناك مشكلة لا تستطيع الحذف الان", "alert-danger")

    return redirect("main:home_view")


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

