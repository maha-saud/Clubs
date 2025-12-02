from django.contrib import admin
from .models import Gym, Hood, GymComment



class GymAdmin(admin.ModelAdmin):
    list_display = ("user", "has_coach")
    list_filter = ("has_coach", "hoods")


class GymCommentAdmin(admin.ModelAdmin):
    list_display = ("user", "gym", "comment_type", "rating")
    list_filter = ("comment_type", "rating", "gym")




admin.site.register(Gym, GymAdmin)
admin.site.register(GymComment, GymCommentAdmin)
admin.site.register(Hood)            

