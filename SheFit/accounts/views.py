from django.db.models import Value ,CharField
from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate ,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.urls import reverse
from .forms import CoachSignUpForm, TraineeSignUpForm, GymSignUpForm
from .models import Trainee 
from coaches.models import Coach, UserSubscription
from .utils import validate_password_ar
from django.core.exceptions import ValidationError
from gyms.models import Gym,Hood, GymComment
from coaches.models import CoachComment





# Create your views here.
def signup_view (request:HttpRequest):
    return render(request,"accounts/signup.html",{})


def signin_view (request:HttpRequest):
    if request.method =="POST":
        user= authenticate(request, username=request.POST["username"], password=request.POST["password"])

        if user:
            login(request,user)
            messages.success(request,"تم تسجيل الدخول بنجاح", "alert-success")
            return redirect(request.GET.get("next",'/'))
        else:
            messages.error(request, "الرجاء المحاولة مرة اخرى، هناك خطأ في بيانات تسجيل الدخول", "alert-danger")

    return render(request,"accounts/signin.html",{})


def coach_signup_view(request: HttpRequest):
    coach_form = CoachSignUpForm()

    if request.method == "POST":
        try:
            with transaction.atomic():

                password = request.POST["password"]
                validate_password_ar(password)

                coach_form = CoachSignUpForm(request.POST, request.FILES)
                if not coach_form.is_valid():
                    for field in coach_form.errors:
                        for error in coach_form.errors[field]:
                            messages.error(request, error, "alert-danger")
                    return render(
                        request,
                        "accounts/coach_signup.html",
                        {"form": coach_form}
                    )

                # الآن فقط ننشئ المستخدم
                new_user = User.objects.create_user(
                    username=request.POST["username"],
                    first_name=request.POST["first_name"],
                    last_name=request.POST["last_name"],
                    email=request.POST["email"],
                    password=password
                )

                coach = coach_form.save(commit=False)
                coach.user = new_user
                coach.save()

                messages.success(request, "تم تسجيل الحساب بنجاح", "alert-success")
                return redirect("accounts:signin_view")

        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg, "alert-danger")

        except IntegrityError:
            messages.error(
                request,
                "اسم المستخدم مستخدم بالفعل، يرجى إدخال اسم آخر",
                "alert-danger"
            )

        except Exception as e:
            messages.error(
                request,
                f"حدث خطأ أثناء التسجيل {str(e)}",
                "alert-warning"
            )

    return render(request, "accounts/coach_signup.html", {"form": coach_form})


def trainee_signup_view(request: HttpRequest):
    trainee_form = TraineeSignUpForm()

    if request.method == "POST":
        try:
            with transaction.atomic():

                password = request.POST["password"]
                validate_password_ar(password)

                trainee_form = TraineeSignUpForm(request.POST, request.FILES)
                if not trainee_form.is_valid():
                    for field in trainee_form.errors:
                        for error in trainee_form.errors[field]:
                            messages.error(request, error, "alert-danger")
                    return render(
                        request,
                        "accounts/trainee_signup.html",
                        {"form": trainee_form}
                    )

                new_user = User.objects.create_user(
                    username=request.POST["username"],
                    first_name=request.POST["first_name"],
                    last_name=request.POST["last_name"],
                    email=request.POST["email"],
                    password=password
                )


                trainee = trainee_form.save(commit=False)
                trainee.user = new_user
                trainee.save()

                messages.success(request, "تم تسجيل الحساب بنجاح", "alert-success")
                return redirect("accounts:signin_view")

        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg, "alert-danger")

        except IntegrityError:
            messages.error(
                request,
                "اسم المستخدم مستخدم بالفعل، يرجى إدخال اسم آخر",
                "alert-danger"
            )

        except Exception as e:
            messages.error(
                request,
                f"حدث خطأ أثناء التسجيل {str(e)}",
                "alert-warning"
            )

    return render(request, "accounts/trainee_signup.html", {"form": trainee_form})

def gym_signup_view(request: HttpRequest):
    gym_form = GymSignUpForm()
    hoods = Hood.objects.all()

    if request.method == "POST":
        try:
            with transaction.atomic():

                #  فحص كلمة المرور أولاً
                password = request.POST["password"]
                validate_password_ar(password)

                #  التحقق من الفورم قبل الإنشاء 
                gym_form = GymSignUpForm(request.POST, request.FILES)
                if not gym_form.is_valid():
                    for field in gym_form.errors:
                        for error in gym_form.errors[field]:
                            messages.error(request, error, "alert-danger")
                    return render(
                        request,
                        "accounts/gym_signup.html",
                        {"form": gym_form, "hood": hoods}
                    )

                #  إنشاء يوزر بعد نجاح كل التحقق
                new_user = User.objects.create_user(
                    username=request.POST["username"],
                    email=request.POST["email"],
                    password=password
                )

                #  إنشاء النادي
                gym = gym_form.save(commit=False)
                gym.user = new_user
                gym.has_coach = request.POST.get("has_coach") == "True"
                gym.save()

                #  حفظ الأحياء
                selected_hoods = request.POST.getlist("hoods")
                gym.hoods.set(selected_hoods)

                messages.success(request, "تم تسجيل النادي بنجاح", "alert-success")
                return redirect("accounts:signin_view")

        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg, "alert-danger")

        except IntegrityError:
            messages.error(
                request,
                "حدث خطأ في إنشاء الحساب، قد يكون اسم المستخدم مستخدم مسبقًا",
                "alert-danger"
            )

        except Exception as e:
            messages.error(
                request,
                f"حدث خطأ أثناء التسجيل {str(e)}",
                "alert-warning"
            )

    return render(
        request,
        "accounts/gym_signup.html",
        {"form": gym_form, "hood": hoods}
    )


def logout_view (request:HttpRequest):
    logout(request)
    messages.success(request, "تم تسجيل خروج بنجاح", "alert-warning")

    return redirect(request.GET.get("next","/"))



def profile_trainee_view(request:HttpRequest, train_id:int):
    trainee=Trainee.objects.get(pk=train_id)
    active_tab = request.GET.get('tab','favorite_coaches')
    favorite_coaches = trainee.favorite_coaches.all() if active_tab == 'favorite_coaches' else None
    coach_comments = CoachComment.objects.filter(user=trainee.user).order_by('-created_at')
    gym_comments = GymComment.objects.filter(user=trainee.user).order_by('-created_at')
    subscriptions = UserSubscription.objects.filter(trainee=trainee).select_related('plan','plan__coach')

    context = {
        "trainee":trainee,
        'active_tab':active_tab,
        'favorite_coaches':favorite_coaches,
        'subscriptions':subscriptions,
        "coach_comments": coach_comments,
        "gym_comments": gym_comments,
    }
    return render(request,"accounts/profile_trainee.html", context)

@login_required
def add_favorite_coaches_view (request:HttpRequest, coach_id:int):
    try:
        coach = Coach.objects.get(pk=coach_id)
        trainee= request.user.trainee
        
        if coach not in trainee.favorite_coaches.all():
            trainee.favorite_coaches.add(coach)
            messages.success(request, "تم إضافة الى المفضلة","alert-success")
        else:
            trainee.favorite_coaches.remove(coach)
            messages.warning(request, "تم الإزالة من المفضلة","alert-warning")  

    except Exception as e:
        messages.error(request, "المدرب غير موجود","alert-error")  
    return redirect(request.META.get('HTTP_REFERER'),"coaches:profile_coach_view" ,coach_id=coach_id)

