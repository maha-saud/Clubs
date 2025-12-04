from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib import messages
from .models import Coach, CoachComment ,SubscriptionPlan, UserSubscription
from .forms import SubscriptionPlanForm
from django.db.models import Count, Avg
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

# Create your views here.
def all_coaches_view(request:HttpRequest):
    coaches= Coach.objects.all().annotate(avg_rating=Avg("coachcomment__rating"),comments_count=Count("coachcomment"))

    # فلترة التقييم
    rating_order = request.GET.get("rating", "all")
    if rating_order == "high":
        coaches = coaches.order_by("-avg_rating")
    elif rating_order == "low":
        coaches = coaches.order_by("avg_rating")
 
    # فلترة السعر
    price_order = request.GET.get("price", "all")
    if price_order == "high":
        coaches = coaches.order_by("-price")
    elif price_order == "low":
        coaches = coaches.order_by("price")
    
    # فلترة الخبرة
    experience_order = request.GET.get("experience_years", "all")
    if experience_order == "high":
        coaches = coaches.order_by("-experience_years")
    elif experience_order == "low":
        coaches = coaches.order_by("experience_years")

    # Pagination
    page_number = request.GET.get("page", 1)
    paginator = Paginator(coaches, 6)
    coaches_page = paginator.get_page(page_number)
    return render(request,"coaches/all_coaches.html",{"coaches":coaches,"coach_page":coaches_page, "selected_rating": rating_order ,"selected_price": price_order , "selected_experience": experience_order})

def profile_coach_view(request:HttpRequest, coach_id:int):
    coach=Coach.objects.get(pk=coach_id)
    related_coaches= Coach.objects.all().exclude(pk=coach_id)[0:4]
    return render(request,"coaches/profile_coach.html", {"coach":coach,"related_coaches":related_coaches})

def coach_update_view(request: HttpRequest, coach_id: int):
    try:
        coach=Coach.objects.get(pk=coach_id)
    except Coach.DoesNotExist:
        messages.error(request, "المدرب غير موجود", "alert-warning")   
         
    if request.user != coach.user and not request.user.is_staff:
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

@login_required
def add_plan_view(request:HttpRequest):
    try:
        coach= request.user.coach
    except Coach.DoesNotExist:
        messages.error(request,"يجب أن تكون مدرب لإنشاء باقات","alert-danger")
        return redirect("accounts:coach_signup_view") 

    if request.method == "POST":
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.coach = coach
            plan.save()
            messages.success(request, "تم إضافة الباقة بنجاح", "alert-success")
    else:
        form = SubscriptionPlanForm()

    return render(request, "coaches/add_plan.html",{"form":form}) 

def update_plan_view(request:HttpRequest, plan_id):
    try:
        coach= request.user.coach
        plan=SubscriptionPlan.objects.get(pk=plan_id)
    except Coach.DoesNotExist:
        messages.error(request, "الخطة غير موجودة", "alert-warning") 
        return redirect("coach:plans_list_view")

         
    if request.user != coach.user:
        messages.warning(request,"فقط يمكن لصاحب الحساب التعديل","alert-warning")
        return redirect("coach:plans_list_view")
    
    if request.method =="POST":
        plan.name = request.POST.get("name", plan.name)
        plan.description = request.POST.get("description", plan.description)
        plan.duration_days = request.POST.get("duration_days",plan.duration_days)
        plan.price = request.POST.get("price",plan.price)
        plan.max_subscribers = request.POST.get("max_subscribers",plan.max_subscribers)
        plan.save()

        messages.success(request,"تم تحديث الخطة بنجاح", "alert-success")
        return redirect("coaches:plans_list_view" ,coach_id=coach.id)
    return render(request,"coaches/update_plan.html", {"plan":plan} )

def delete_plan_view(request:HttpRequest, plan_id):
    try:
        coach= request.user.coach
    except Coach.DoesNotExist:
        messages.error(request, "الخطة غير موجودة", "alert-warning") 
        return redirect("coach:plans_list_view")

    if request.user != coach.user:
        messages.warning(request, "فقط يمكن لصاحب الخطة الحذف", "alert-warning")
        return redirect("main:home_view")

    try:
        plan = SubscriptionPlan.objects.get(pk=plan_id)
        plan.delete()
        messages.success(request, "تم حذف الخطة بنجاح", "alert-success")

    except Exception as e:
        messages.error(request, "هناك مشكلة لا تستطيع الحذف الان", "alert-danger")

    return redirect("coach:plans_list_view")

def plans_list_view(request:HttpRequest, coach_id): 
    coach = get_object_or_404(Coach, pk =coach_id) 
    plans = SubscriptionPlan.objects.filter(coach=coach)
    return render(request, "coaches/plans_list.html", {"coach":coach, "plans":plans})

@login_required
def subcribe_view(request:HttpRequest, plan_id):
    try:
        plan =SubscriptionPlan.objects.get(pk=plan_id)

    except SubscriptionPlan.DoesNotExist:
        messages.error(request,"الباقة غير موجودة","alert-danger")
        return redirect("coaches:plans_list") 
    
    #التحقق من عدد المقاعد
    if plan.remaining <= 0:
        messages.error(request,"عذرا، اكتمل عدد المشتركين في هذه الباقة.", "alert-warning")
        return redirect("coaches:plans_list") 

    # تحديث العدد
    plan.current_subscribers +=1
    plan.save()

    #إنشاء اشتراك
    UserSubscription.objects.create(user= request.user, plan= plan)
    messages.success(request, "تم الاشتراك بنجاح", "alert-success")
    return redirect("coaches:profile_coach")


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

