from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.contrib import messages
from .models import Gym, Hood, GymComment
from .forms import GymForm
from coaches.models import Coach

# Create your views here. 


def all_gyms_view(request: HttpRequest, hood_name):

    #gyms = Gym.objects.all().annotate(avg_rating=Avg("comments__rating"),comments_count=Count("comments") )


    gyms = (
        Gym.objects
        .annotate(
            avg_rating=Avg("comments__rating"),
            comments_count=Count("comments", filter=Q(comments__parent__isnull=True))
        )
    )

    # لو طلب حي معين
    if hood_name != "all":
        gyms = gyms.filter(hoods__name=hood_name)

    # فلترة التقييم
    rating_order = request.GET.get("rating", "all")
    if rating_order == "high":
        gyms = gyms.order_by("-avg_rating")
    elif rating_order == "low":
        gyms = gyms.order_by("avg_rating")

    # فلترة وجود مدربين
    has_coach = request.GET.get("has_coach", "all")
    if has_coach == "yes":
        gyms = gyms.filter(has_coach=True)
    elif has_coach == "no":
        gyms = gyms.filter(has_coach=False)

    # فلترة حسب الحي
    hood_id = request.GET.get("hood", "all")
    if hood_id != "all" and hood_id != "":
        gyms = gyms.filter(hoods__id=hood_id)

    # فلترة السعر
    price_sort = request.GET.get("price", "all")

    if price_sort == "low":
        gyms = gyms.order_by("monthly_price")  # الأرخص أولاً
    elif price_sort == "high":
        gyms = gyms.order_by("-monthly_price")  # الأغلى أولاً

    # Pagination
    page_number = request.GET.get("page", 1)
    paginator = Paginator(gyms, 6 )
    gyms_page = paginator.get_page(page_number)

    #parent_comments_count=Count("comments", filter=Q(comments__parent__isnull=True))



    return render(request, "gyms/all_gyms.html", {
        "gyms": gyms_page,
        "hoods": Hood.objects.all(),
        "current_hood": hood_name,

        "selected_rating": rating_order,
        "selected_has_coach": has_coach,
        "selected_hood": str(hood_id),
        "selected_price": price_sort,
    }) 


def gym_detail_view(request: HttpRequest, gym_id: int):

    gym = get_object_or_404(Gym, pk=gym_id)

    # متوسط التقييم (فقط للتعليقات الأساسية اللي فيها تقييم)
    avg = (
        gym.comments
           .filter(parent__isnull=True, rating__isnull=False)
           .aggregate(Avg("rating"))
    )

    # التعليقات الأساسية (parent = NULL) مع المستخدم والردود
    parent_comments = (
    gym.comments
       .filter(parent__isnull=True)
       .select_related("user")
       .prefetch_related("replies__user", "replies__reply_to")
       .order_by("-created_at")
)



    coaches = gym.coaches.all()

    return render(
        request,
        "gyms/gym_detail.html",
        {
            "gym": gym,
            "average_rating": avg["rating__avg"],
            "coaches": coaches,
            "parent_comments": parent_comments,   # هذا المهم
        },
    )



def gym_update_view(request: HttpRequest, gym_id: int):

    # نجيب بيانات النادي
    gym = Gym.objects.get(pk=gym_id)
    hoods = Hood.objects.all()   # نعرض كل الأحياء


    # بس الستاف يقدرون يعدلون
    if not request.user.is_staff and request.user != gym.user :
        messages.warning(request, "Only staff can update gym", "alert-warning")
        return redirect("main:home_view")


    if request.method == "POST":

        # لو غيّر الصورة
        if "image" in request.FILES:
            gym.image = request.FILES["image"]
        # تحديث الاسم
        gym.name = request.POST.get("name")


        # تحديث الأحياء (ManyToMany)
        selected_hoods = request.POST.getlist("hoods")
        gym.hoods.set(selected_hoods)

        # تحديث هل يوجد مدربين
        gym.has_coach = True if request.POST.get("has_coach") == "true" else False

        # تحديث الوصف
        gym.about = request.POST.get("about")

        # السعر و الموقع 
        gym.monthly_price = request.POST.get("monthly_price")   
        gym.website = request.POST.get("website") 

        # نحفظ التعديل
        gym.save()

        messages.success(request, "تم تحديث بيانات النادي بنجاح", "alert-success")
        return redirect("gyms:gym_detail_view", gym_id=gym.id)

    return render(request, "gyms/gym_update.html", {
        "gym": gym,
        "hoods": hoods,
    })

def gym_delete_view(request: HttpRequest, gym_id: int):

   

    try:
        # نحاول نجيب النادي ونحذفه
        gym = Gym.objects.get(pk=gym_id)
        gym.delete()
        messages.success(request, "Deleted gym successfully", "alert-success")

    except Exception as e:
        # لو صار خطأ
        messages.error(request, "Couldn't delete gym", "alert-danger")

 # فقط الإدمن يقدر يحذف
    if not request.user.is_staff and request.user != gym.user :
        messages.warning(request, "only staff can delete gym", "alert-warning")
        return redirect("main:home_view")
    # نرجع للصفحة الرئيسية
    return redirect("main:home_view")

def add_comment_view(request: HttpRequest, gym_id: int):

    if not request.user.is_authenticated:
        messages.error(request, "يجب تسجيل الدخول أولاً")
        return redirect("accounts:sign_in")

    if request.method == "POST":
        gym_object = get_object_or_404(Gym, pk=gym_id)

        parent_id = request.POST.get("parent")
        parent_comment = None
        reply_to = None

        # لو فيه parent معناته هذا رد
        if parent_id:
            parent_comment = get_object_or_404(GymComment, pk=parent_id)
            reply_to = parent_comment.user   # عشان المنشن

        # لو تعليق رئيسي  نأخذ التقييم و النوع
        if parent_comment is None:
            rating_value = request.POST.get("rating") or None
            comment_type_value = request.POST.get("comment_type") or None
        else:
            rating_value = None
            comment_type_value = None

        GymComment.objects.create(
            gym=gym_object,
            user=request.user,
            comment=request.POST["comment"],
            rating=rating_value,
            comment_type=comment_type_value,
            parent=parent_comment,
            reply_to=reply_to,
        )

        messages.success(request, "تم إضافة تعليقك بنجاح ❤️", "alert-success")

    return redirect("gyms:gym_detail_view", gym_id=gym_id)



def add_reply_view(request: HttpRequest, comment_id: int):

    # لو مو مسجّل دخول نرجعه لتسجيل الدخول
    if not request.user.is_authenticated:
        messages.error(request, "لا يمكنك الرد على التعليقات الا في حال تسجيل الدخول", "alert-danger")
        return redirect("accounts:sign_in")

    # نجيب التعليق الأساسي اللي بنرد عليه
    parent_comment = GymComment.objects.get(pk=comment_id)

    if request.method == "POST":

        # نسوي رد جديد كتسجيل تعليق عادي بس مربوط بالتعليق الأساسي
        GymComment.objects.create(
            gym=parent_comment.gym, # نفس النادي حق التعليق الأساسي
            user=request.user, # اللي كتب الرد
            parent=parent_comment, # هذا أهم شي الربط كرد
            comment=request.POST["reply_text"],  # نص الرد
            comment_type=None,  # نخلي نوعه نفس نوع التعليق الأساسي
            rating=None                          # الرد ما له تقييم
        )

        messages.success(request, "تم إضافة الرد بنجاح", "alert-success")

    # نرجع لصفحة تفاصيل النادي
    return redirect("gyms:gym_detail_view", gym_id=parent_comment.gym.id)



def toggle_coach_gym(request, gym_id):
    if not request.user.is_authenticated:
        messages.error(request, "يجب تسجيل الدخول.")
        return redirect("accounts:sign_in")

    # المدرب نفسه
    try:
        coach = request.user.coach
    except:
        messages.error(request, "هذا الخيار خاص بالمدربين فقط.")
        return redirect("gyms:gym_detail_view", gym_id=gym_id)

    gym = get_object_or_404(Gym, pk=gym_id)

    # لو المدرب غير منتسب لأي نادي
    if coach.gym is None:
        coach.gym = gym
        coach.save()
        messages.success(request, f"تم انتسابك لنادي {gym.user.username} بنجاح!")
    
    # لو المدرب منتسب لنفس النادي  يلغي
    elif coach.gym == gym:
        coach.gym = None
        coach.save()
        messages.success(request, "تم إلغاء الانتساب من النادي.")

    # لو المدرب منتسب لنادي آخر
    else:
        messages.error(request, "لا يمكنك الانتساب لأكثر من نادي .")

    return redirect("gyms:gym_detail_view", gym_id=gym_id)



def delete_comment_view(request, comment_id):
    comment = get_object_or_404(GymComment, pk=comment_id)

    # السماح بالحذف فقط لصاحبه، أو صاحب النادي، أو موظف
    if request.user != comment.user and request.user != comment.gym.user and not request.user.is_staff:
        messages.error(request, "لا يمكنك حذف هذا التعليق.")
        return redirect("gyms:gym_detail_view", gym_id=comment.gym.id)

    gym_id = comment.gym.id
    comment.delete()

    messages.success(request, "تم حذف التعليق.")
    return redirect("gyms:gym_detail_view", gym_id=gym_id)