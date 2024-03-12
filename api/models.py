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


class WeeklyAmount(models.Model):
    saving_plan = models.ForeignKey(
        SavingPlan, on_delete=models.CASCADE, related_name='amount_list')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    selected = models.BooleanField(default=False)
    week_index = models.IntegerField(default=0)
    date_selected = models.DateField()
