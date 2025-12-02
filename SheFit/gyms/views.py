from django.shortcuts import render, redirect
from django.db.models import Count, Avg
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.contrib import messages
from .models import Gym, Hood, GymComment
from .forms import GymForm
from coaches.models import Coach

# Create your views here. 


def all_gyms_view(request: HttpRequest, hood_name):

    gyms = Gym.objects.all().annotate(
        avg_rating=Avg("comments__rating"),
        comments_count=Count("comments")
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

    # Pagination
    page_number = request.GET.get("page", 1)
    paginator = Paginator(gyms, 6)
    gyms_page = paginator.get_page(page_number)

    return render(request, "gyms/all_gyms.html", {
        "gyms": gyms_page,
        "hoods": Hood.objects.all(),
        "current_hood": hood_name,

        "selected_rating": rating_order,
        "selected_has_coach": has_coach,
        "selected_hood": str(hood_id),
    }) # اخر ثلاث عشان الفلتره تحتفظ بالي حددته 

def gym_detail_view(request: HttpRequest, gym_id: int):

    # نجيب النادي حسب الـ id
    gym = Gym.objects.get(pk=gym_id)

    # نحسب متوسط تقييمات النادي
    avg = gym.comments.all().aggregate(Avg("rating"))

    # نجيب المدربين اللي بالنادي
    coaches = gym.coaches.all()

    # نرسل البيانات للصفحة
    return render(request, "gyms/gym_detail.html", {
        "gym": gym,
        "average_rating": avg["rating__avg"],
        "coaches": coaches
    })



def gym_update_view(request: HttpRequest, gym_id: int):

    # بس الستاف يقدرون يعدلون
    if not (request.user.is_staff and request.user.has_perm("gyms.change_gym")):
        messages.warning(request, "Only staff can update gym", "alert-warning")
        return redirect("main:home_view")

    # نجيب بيانات النادي
    gym = Gym.objects.get(pk=gym_id)
    hoods = Hood.objects.all()   # نعرض كل الأحياء

    if request.method == "POST":

        # لو غيّر الصورة
        if "image" in request.FILES:
            gym.image = request.FILES["image"]

        # تحديث الأحياء (ManyToMany)
        selected_hoods = request.POST.getlist("hoods")
        gym.hoods.set(selected_hoods)

        # تحديث هل يوجد مدربين
        gym.has_coach = True if request.POST.get("has_coach") == "true" else False

        # تحديث الوصف
        gym.about = request.POST.get("about")

        # نحفظ التعديل
        gym.save()

        messages.success(request, "تم تحديث بيانات النادي بنجاح", "alert-success")
        return redirect("gyms:gym_detail_view", gym_id=gym.id)

    return render(request, "gyms/gym_update.html", {
        "gym": gym,
        "hoods": hoods,
    })

def gym_delete_view(request: HttpRequest, gym_id: int):

    # فقط الإدمن يقدر يحذف
    if not request.user.is_staff:
        messages.warning(request, "only staff can delete gym", "alert-warning")
        return redirect("main:home_view")

    try:
        # نحاول نجيب النادي ونحذفه
        gym = Gym.objects.get(pk=gym_id)
        gym.delete()
        messages.success(request, "Deleted gym successfully", "alert-success")

    except Exception as e:
        # لو صار خطأ
        messages.error(request, "Couldn't delete gym", "alert-danger")

    # نرجع للصفحة الرئيسية
    return redirect("main:home_view")


def add_comment_view(request: HttpRequest, gym_id):

    # اذا المستخدم مو مسجّل دخول
    if not request.user.is_authenticated:
        messages.error(request, "Only registered users can add comments", "alert-danger")
        return redirect("accounts:sign_in")

    # اذا جتنا بيانات الفورم
    if request.method == "POST":

        # نجيب النادي اللي بنضيف له تعليق
        gym_object = Gym.objects.get(pk=gym_id)

        # نسوي تعليق جديد من البيانات اللي ارسلها المستخدم
        new_comment = GymComment(
            gym=gym_object,
            user=request.user,
            comment=request.POST["comment"],
            rating=request.POST["rating"],
            comment_type=request.POST["comment_type"]
        )

        # نحفظ التعليق
        new_comment.save()

        # نعطي رسالة نجاح
        messages.success(request, "تم إضافة التعليق بنجاح", "alert-success")

    # نرجع لصفحة تفاصيل النادي
    return redirect("gyms:gym_detail_view", gym_id=gym_id)
