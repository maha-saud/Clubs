from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate ,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction
from .forms import CoachSignUpForm, TraineeSignUpForm, GymSignUpForm
from .models import Trainee 
from coaches.models import Coach, UserSubscription
from gyms.models import Gym
from gyms.models import Hood




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
            messages.error(request, "الرجاء المحاولة مرة اخرى، هناك خطأ في بيانات تسجيل الدخول", "alert-wrong")

    return render(request,"accounts/signin.html",{})


def coach_signup_view (request:HttpRequest):
    coach_form=CoachSignUpForm()
    if request.method =="POST":
        try:
            with transaction.atomic():
                new_user =User.objects.create_user(username=request.POST["username"], first_name=request.POST["first_name"], last_name=request.POST["last_name"], email=request.POST["email"], password=request.POST["password"])

                coach_form=CoachSignUpForm(request.POST, request.FILES)
                if coach_form.is_valid():
                    coach = coach_form.save(commit=False)
                    coach.user = new_user
                    coach.save()
                else:
                    raise IntegrityError("هناك خطأ في بيانات المدرب")

                messages.success(request, "تم تسجيل الحساب بنجاح", "alert-success")
                return redirect('accounts:signin_view')
        except IntegrityError as e:
            messages.error(request, "اسم المستخدم مستخدم بالفعل، الرجالء ادخال اخر", "alert-danger")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء التسجيل {str(e)}", "alert-warning")  

    return render(request,"accounts/coach_signup.html",{"form":coach_form})


def trainee_signup_view (request:HttpRequest):
    trainee_form=TraineeSignUpForm()
    if request.method =="POST":
        try:
            with transaction.atomic():
                new_user =User.objects.create_user(username=request.POST["username"], first_name=request.POST["first_name"], last_name=request.POST["last_name"], email=request.POST["email"], password=request.POST["password"])

                trainee_form=TraineeSignUpForm(request.POST, request.FILES)
                if trainee_form.is_valid():
                    trainee = trainee_form.save(commit=False)
                    trainee.user = new_user
                    trainee.save()
                else:
                    raise IntegrityError("هناك خطأ في بيانات المتدرب")

                messages.success(request, "تم تسجيل الحساب بنجاح", "alert-success")
                return redirect('accounts:signin_view')
            
        except IntegrityError as e:
            messages.error(request, "اسم المستخدم مستخدم بالفعل، الرجالء ادخال اخر", "alert-danger")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء التسجيل {str(e)}", "alert-warning")  

    return render(request,"accounts/trainee_signup.html",{"form":trainee_form})

def gym_signup_view (request:HttpRequest):
    gym_form=GymSignUpForm()
    hoods = Hood.objects.all()
    if request.method =="POST":
        try:
            with transaction.atomic():
                new_user =User.objects.create_user(username=request.POST["username"], email=request.POST["email"], password=request.POST["password"])
                
                gym_form=GymSignUpForm(request.POST, request.FILES)
                if gym_form.is_valid():
                    gym = gym_form.save(commit=False)
                    gym.user = new_user
                    gym.has_coach = request.POST.get("has_coach") == "True"
                    gym.save()

                    selected_hoods = request.POST.getlist('hoods')
                    gym.hoods.set(selected_hoods)
                else:
                    raise IntegrityError("هناك خطأ في بيانات النادي")

                messages.success(request, "تم تسجيل النادي بنجاح", "alert-success")
                return redirect('accounts:signin_view')
        except IntegrityError as e:
            messages.error(request, str(e), "alert-danger")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء التسجيل {str(e)}", "alert-warning")  

    return render(request,"accounts/gym_signup.html",{"form":gym_form, "hood":hoods})


def logout_view (request:HttpRequest):
    logout(request)
    messages.success(request, "تم تسجيل خروج بنجاح", "alert-warning")

    return redirect(request.GET.get("next","/"))



def profile_trainee_view(request:HttpRequest, train_id:int):
    trainee=Trainee.objects.get(pk=train_id)
    active_tab = request.GET.get('tab','favorite_coaches')
    favorite_coaches = trainee.favorite_coaches.all() if active_tab == 'favorite_coaches' else None
    favorite_gyms = trainee.favorite_gyms.all() if active_tab == 'favorite_gyms' else None
    subscriptions = UserSubscription.objects.filter(trainee=trainee).select_related('plan','plan__coach')

    context = {
        "trainee":trainee,
        'active_tab':active_tab,
        'favorite_coaches':favorite_coaches,
        'favorite_gyms':favorite_gyms,
        'subscriptions':subscriptions,
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

@login_required
def add_favorite_gyms_view (request:HttpRequest, gym_id:int):
    try:
        gym = Gym.objects.get(pk=gym_id)
        trainee= request.user.trainee
        
        if gym not in trainee.favorite_gyms.all():
            trainee.favorite_gyms.add(gym)
            messages.success(request, "تم إضافة الى المفضلة","alert-success")
        else:
            trainee.favorite_gyms.remove(gym)
            messages.warning(request, "تم الإزالة من المفضلة","alert-warning")  

    except Exception as e:
        messages.error(request, "النادي غير موجود","alert-error")  
    return redirect(request.META.get('HTTP_REFERER'),"gyms:gym_detail_view" ,gym_id=gym_id)
