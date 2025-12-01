from django.contrib import admin
from .models import Gym ,Hood
from coaches.models import Coach




# Register your models here.

class GymAdmin(admin.ModelAdmin):
    list_display=("username",) 

    def username(self, obj):
        return obj.user.username
    username.short_description =username 

class HoodAdmin  (admin.ModelAdmin):
    list_display=("name",)  



class CoachAdmin(admin.ModelAdmin):
    list_display=("username",) 

    def username(self, obj):
        return obj.user.username
    username.short_description =username   


admin.site.register(Gym,GymAdmin)
admin.site.register(Hood,HoodAdmin)
admin.site.register(Coach,CoachAdmin)



