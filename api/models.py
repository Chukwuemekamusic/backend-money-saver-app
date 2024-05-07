from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    username = models.CharField(max_length=150, default='ignore')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.first_name


class SavingPlan(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='saving_plans')
    savings_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    number_of_weeks = models.IntegerField(default=52)

    @property
    def total_saved_amount(self):
        return self.amount_list.filter(selected=True).aggregate(models.Sum('amount'))['amount__sum'] or 0
    
    
    # def selected_weekly_amounts(self):
    #     return self.amount_list.filter(selected=True)



class WeeklyAmount(models.Model):
    saving_plan = models.ForeignKey(
        SavingPlan, on_delete=models.CASCADE, related_name='amount_list')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    selected = models.BooleanField(default=False)
    week_index = models.IntegerField(default=0)
    date_selected = models.DateTimeField(null=True, blank=True)  # added Time
    # date_selected = models.DateField(auto_now_add=True)
