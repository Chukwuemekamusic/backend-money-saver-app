from rest_framework import serializers
from .models import CustomUser, SavingPlan, WeeklyAmount
from rest_framework.serializers import (ModelSerializer)
from django.contrib.auth import authenticate


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = f"{validated_data['first_name']}_{validated_data['last_name']}"
        validated_data['username'] = username
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

    # def validate(self, data):
    #     user = authenticate(**data)
    #     if user and user.is_active:
    #         return user
    #     raise serializers.ValidationError("Invalid Details.")

    def validate(self, attrs):
        email = attrs.get('email').lower()
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                'Please provide both email and password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid email or password.')

        return user


class WeeklyAmountSerializer(ModelSerializer):
    class Meta:
        model = WeeklyAmount
        fields = ['id', 'amount', 'selected', 'week_index',
                  'date_selected']


class SavingPlanSerializer(ModelSerializer):
    amount_list = WeeklyAmountSerializer(many=True)

    class Meta:
        model = SavingPlan
        fields = ['id', 'user', 'savings_name',
                  'amount', 'date_created', 'amount_list']

    def create(self, validated_data):
        amount_list_data = validated_data.pop('amount_list')
        # validated_data['user'] = self.request.user
        saving_plan = SavingPlan.objects.create(**validated_data)

        for amount_data in amount_list_data:
            WeeklyAmount.objects.create(saving_plan=saving_plan, **amount_data)
        return saving_plan

# update weeklyAmount
