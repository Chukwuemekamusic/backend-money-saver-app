# Generated by Django 4.2 on 2024-08-07 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_savingplan_number_of_weeks'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='registration_method',
            field=models.CharField(choices=[('email', 'Email'), ('google', 'Google')], default='email', max_length=10),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
