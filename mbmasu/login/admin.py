from django.contrib import admin
from .models import Company, UserProfile, Role

# Register your models here.

admin.site.register(Company)
admin.site.register(Role)
admin.site.register(UserProfile)

