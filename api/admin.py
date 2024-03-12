from django.contrib import admin
from .models import CustomUser, SavingPlan, WeeklyAmount

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(SavingPlan)
admin.site.register(WeeklyAmount)
