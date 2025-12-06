from django.db import models

# Create your models here.

class Contact(models.Model):
    TYPE_CONTACT = [
        ('inquiry','استفسار'),
        ('suggestion', 'اقتراح'),
        ('help', 'طلب مساعدة'),
        ('complaint', 'شكوى'),
    ]  
    first_name =models.CharField(max_length=2048)
    last_name =models.CharField(max_length=2048)
    email =models.EmailField()
    type = models.CharField(max_length=20, choices=TYPE_CONTACT ,default='inquiry')
    message= models.TextField()
    created_at= models.DateTimeField(auto_now_add=True)
