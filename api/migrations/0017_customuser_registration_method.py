# Generated by Django 4.2 on 2024-08-08 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_remove_customuser_registration_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='registration_method',
            field=models.CharField(choices=[('email', 'Email'), ('google', 'Google')], default='google', max_length=10),
        ),
    ]
