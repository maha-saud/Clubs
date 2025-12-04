from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate ,login,logout
from django.contrib import messages
from .forms import CoachSignUpForm, TraineeSignUpForm, GymSignUpForm
from .models import Trainee
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
            new_user =User.objects.create_user(username=request.POST["username"], first_name=request.POST["first_name"], last_name=request.POST["last_name"], email=request.POST["email"], password=request.POST["password"])
            new_user.save()

            coach_form=CoachSignUpForm(request.POST, request.FILES)
            if coach_form.is_valid():
                coach = coach_form.save(commit=False)
                coach.user = new_user
                coach.save()
                messages.success(request, "تم تسجيل الحساب بنجاح", "alert-success")
                return redirect('accounts:signin_view')
            else:
                messages.error(request, "هناك خطأ في بيانات المدرب", "alert-warning")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء التسجيل {str(e)}", "alert-warning")  

    return render(request,"accounts/coach_signup.html",{"form":coach_form})


def trainee_signup_view (request:HttpRequest):
    trainee_form=TraineeSignUpForm()
    if request.method =="POST":
        try:
            new_user =User.objects.create_user(username=request.POST["username"], first_name=request.POST["first_name"], last_name=request.POST["last_name"], email=request.POST["email"], password=request.POST["password"])
            new_user.save()

            trainee_form=TraineeSignUpForm(request.POST, request.FILES)
            if trainee_form.is_valid():
                trainee = trainee_form.save(commit=False)
                trainee.user = new_user
                trainee.save()
                messages.success(request, "تم تسجيل الحساب بنجاح", "alert-success")
                return redirect('accounts:signin_view')
            else:
                messages.error(request, "هناك خطأ في بيانات المتدرب", "alert-warning")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء التسجيل {str(e)}", "alert-warning")  

    return render(request,"accounts/trainee_signup.html",{"form":trainee_form})

def gym_signup_view (request:HttpRequest):
    gym_form=GymSignUpForm()
    hoods = Hood.objects.all()
    if request.method =="POST":
        try:
            new_user =User.objects.create_user(username=request.POST["username"], email=request.POST["email"], password=request.POST["password"])
            new_user.save()

            gym_form=GymSignUpForm(request.POST, request.FILES)
            if gym_form.is_valid():
                gym = gym_form.save(commit=False)
                gym.user = new_user
                gym.has_coach = request.POST.get("has_coach") == "True"
                gym.save()

                selected_hoods = request.POST.getlist('hoods')
                gym.hoods.set(selected_hoods)

                messages.success(request, "تم تسجيل النادي بنجاح", "alert-success")
                return redirect('accounts:signin_view')
            else:
                messages.error(request, "هناك خطأ في بيانات النادي", "alert-warning")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء التسجيل {str(e)}", "alert-warning")  

    return render(request,"accounts/gym_signup.html",{"form":gym_form, "hood":hoods})


def logout_view (request:HttpRequest):
    logout(request)
    messages.success(request, "تم تسجيل خروج بنجاح", "alert-warning")

    return redirect(request.GET.get("next","/"))


def profile_trainee_view(request:HttpRequest, train_id:int):
    trainee=Trainee.objects.get(pk=train_id)
    return render(request,"accounts/profile_trainee.html", {"trainee":trainee})


