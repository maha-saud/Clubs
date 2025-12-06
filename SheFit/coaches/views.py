from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib import messages
from .models import Coach, CoachComment ,SubscriptionPlan, UserSubscription, Post
from accounts.models import Trainee
from .forms import SubscriptionPlanForm, PostForm
from django.db.models import Count, Avg
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import stripe
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

# Create your views here.
def all_coaches_view(request:HttpRequest):
    coaches= Coach.objects.all().annotate(avg_rating=Avg("coachcomment__rating"),comments_count=Count("coachcomment"))

    # فلترة التقييم
    rating_order = request.GET.get("rating", "all")
    if rating_order == "high":
        coaches = coaches.order_by("-avg_rating")
    elif rating_order == "low":
        coaches = coaches.order_by("avg_rating")
 
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
    return render(request,"coaches/all_coaches.html",{"coaches":coaches,"coach_page":coaches_page, "selected_rating": rating_order , "selected_experience": experience_order})

def profile_coach_view(request:HttpRequest, coach_id:int):
    coach=Coach.objects.get(pk=coach_id)
    #مدربين اخرين
    related_coaches= Coach.objects.all().exclude(pk=coach_id)[0:4]
    #المشتركون وعددهم
    subscribers = UserSubscription.objects.filter(plan__coach = coach).select_related("trainee")[0:4]
    total_subscribers = subscribers.count()
    # المنشورات
    posts = Post.objects.filter(coach=coach)

    return render(request,"coaches/profile_coach.html", {"coach":coach,"related_coaches":related_coaches ,"subscribers":subscribers, "total":total_subscribers,"posts":posts})


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
        coach.website = request.POST.get("website",coach.website)
        coach.about = request.POST.get("about",coach.about)
        
        coach.user.email = request.POST.get("email",coach.user.email)
        coach.user.first_name = request.POST.get("first_name",coach.user.first_name)
        coach.user.last_name = request.POST.get("last_name",coach.user.last_name)
        coach.user.save()


        if "avatar" in request.FILES: coach.avatar = request.FILES["avatar"]
        coach.save()
        messages.success(request,"تم تحديث بيانات المدرب بنجاح", "alert-success")
        return redirect("coaches:profile_coach_view" ,coach_id=coach.id)
    return render(request,"coaches/coach_update.html", {"coach":coach} )

@login_required
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
            return redirect("coach:plans_list_view")
    else:
        form = SubscriptionPlanForm()

    return render(request, "coaches/add_plan.html",{"form":form}) 

@login_required
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

@login_required
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
def checkout_srtipe_view(request:HttpRequest, plan_id):

    stripe.api_key = settings.STRIPE_SECRET_KEY
    #الباقة
    try:
        plan =SubscriptionPlan.objects.get(pk=plan_id)
    except SubscriptionPlan.DoesNotExist:
        messages.error(request,"الباقة غير موجودة","alert-danger")
        return redirect(request.META.get('HTTP_REFERER'),"/")
    
    
    trainee= request.user.trainee


    #التحقق من عدد المقاعد
    if plan.remaining <= 0:
        messages.error(request,"عذرا، اكتمل عدد المشتركين في هذه الباقة.", "alert-warning")
        return redirect(request.META.get('HTTP_REFERER') or "/")
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data":{
                    "currency":"sar",
                    "product_data":{"name":plan.name},
                    "unit_amount":int(plan.price *100),
                },
                "quantity":1,
            } 
        ],
        metadata={
                "plan_id": str(plan.id),
                "trainee_id": str(trainee.id),
        },
        success_url=request.build_absolute_uri(reverse("coaches:payment_success"))+ "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse("coaches:payment_cancel")),
    )
    return redirect(session.url)


@login_required
def payment_success(request:HttpRequest):
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "لا توجد جلسة دفع صالحة", "alert-danger")
        return redirect(request.META.get('HTTP_REFERER') or "/")
    try:
        session =stripe.checkout.Session.retrieve(session_id)
    except Exception:
        messages.error(request,"تعذر التحقق من عملية الدفع","alert-danger")
        return redirect(request.META.get('HTTP_REFERER') or"/")
    #التأكد من ان عملية الدفع تمت
    if session.payment_status != "paid":
        messages.error(request, "لم تكتمل عملية الدفع","alert-warning")
        return redirect(request.META.get('HTTP_REFERER') or "/")
    
    plan_id = session.metadata.get("plan_id")
    trainee_id = session.metadata.get("trainee_id")

    try: 
        plan = SubscriptionPlan.objects.get(pk=plan_id)
        trainee = Trainee.objects.get(pk=trainee_id)

    except (SubscriptionPlan.DoesNotExist, Trainee.DoesNotExist):
        messages.error(request, "حدث خطأ في ربط الاشتراك بالباقة أو الدفعة","alert-danger")
        return redirect(request.META.get('HTTP_REFERER') or "/")
    
        #التحقق من عدد المقاعد
    if plan.remaining <= 0:
        messages.error(request,"عذرا، اكتمل عدد المشتركين في هذه الباقة.", "alert-warning")
        return redirect(request.META.get('HTTP_REFERER') or "/")

    # تحديث العدد
    plan.current_subscribers +=1
    plan.save()

    #إنشاء اشتراك
    UserSubscription.objects.create(trainee= trainee, plan= plan)
    messages.success(request, "تم الاشتراك بنجاح", "alert-success")
    return redirect("coaches:profile_coach_view", coach_id=plan.coach.id)

@login_required
def payment_cancel(request:HttpRequest):
    messages.warning(request, "تم إالغاء عملية الدفع", "alert-warning")
    return redirect(request.META.get('HTTP_REFERER') or "/")
    
@login_required
def add_to_cart_view(request:HttpRequest, plan_id):
    trainee= request.user.trainee
    plan = get_object_or_404(SubscriptionPlan,pk = plan_id)
    #التحقق من ان المتدرب مشترك او لا
    already_subscribed = UserSubscription.objects.filter(trainee=trainee, plan=plan, end_date__gte=timezone.now()).exists()
    if already_subscribed:
        messages.error(request, "أنت مشترك بالفعل في هذه الباقة", "alert-warning")
        return redirect(request.META.get("HTTP_REFERER") or "/")

    request.session["cart"] =plan_id 
    request.session.modified = True
    return redirect("coaches:cart_view") 
  
def cart_view(request:HttpRequest):
    plan_id = request.session.get("cart")
    plan= None
    if plan_id:
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    return render(request, "coaches/cart.html", {"plan":plan})

@login_required
def remove_from_cart_view(request:HttpRequest):

    if "cart"  in request.session:
        del request.session["cart"]
    return redirect("coaches:cart_view")

@login_required
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

# المنشورات
@login_required
def add_post_view(request:HttpRequest):
    try:
        coach= request.user.coach
    except Coach.DoesNotExist:
        messages.error(request,"يجب أن تكون مدرب لإضافة منشور ","alert-danger")
        return redirect("accounts:coach_signup_view") 
    
    if request.method =="POST":
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.coach = coach
            post.save()
            messages.success(request, "تم إضافة منشور بنجاح", "alert-success")
            return redirect("coaches:profile_coach_view" ,coach_id=coach.id)
    else:
        post_form = PostForm()

    return render(request, "coaches/add_post.html")

@login_required
def update_post_view(request:HttpRequest, post_id):
    try:
        coach= request.user.coach
        post=Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        messages.error(request, "المنشور غير موجودة", "alert-warning") 
        return redirect("coaches:profile_coach_view" ,coach_id=coach.id)

         
    if request.user != coach.user:
        messages.warning(request,"فقط يمكن لصاحب الحساب التعديل على المنشور","alert-warning")
        return redirect("coaches:profile_coach_view" ,coach_id=coach.id)
    
    if request.method =="POST":
        post.title = request.POST.get("title", post.title)
        post.content = request.POST.get("content", post.content)
        if "img" in request.FILES: post.img = request.FILES["img"]
        post.save()

        messages.success(request,"تم تحديث المنشور بنجاح", "alert-success")
        return redirect("coaches:profile_coach_view" ,coach_id=coach.id)
    return render(request,"coaches/update_post.html", {"post":post} )

@login_required
def delete_post_view(request:HttpRequest, post_id):
    try:
        coach= request.user.coach
    except Post.DoesNotExist:
        messages.error(request, "المنشور غير موجودة", "alert-warning") 
        return redirect("coaches:profile_coach_view" ,coach_id=coach.id)

    if request.user != coach.user:
        messages.warning(request, "فقط يمكن لصاحب المنشور الحذف", "alert-warning")
        return redirect("coaches:profile_coach_view" ,coach_id=coach.id)

    try:
        post = Post.objects.get(pk=post_id)
        post.delete()
        messages.success(request, "تم حذف المنشور بنجاح", "alert-success")

    except Exception as e:
        messages.error(request, "هناك مشكلة لا تستطيع الحذف الان", "alert-danger")

    return redirect("coaches:profile_coach_view" ,coach_id=coach.id)

