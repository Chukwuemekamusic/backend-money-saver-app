from django.contrib import admin
from .models import CustomUser, SavingPlan, WeeklyAmount

class SavingPlanInline(admin.TabularInline):
    model = SavingPlan
    extra = 1

class CustomUserAdmin(admin.ModelAdmin):
    inlines = [SavingPlanInline]

# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SavingPlan)
admin.site.register(WeeklyAmount)

